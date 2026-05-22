"""Build TradeProposals from Candidates.

For each candidate we attempt to construct vertical credit spreads (and an
iron condor when both sides qualify) at every expiration in the DTE window.
Strike selection drives the rest of the math:

- Index/ETF products: place the short strike outside `index_em_multiplier`
  expected moves.
- Equity names: place it outside `equity_atr_multiplier` ATRs (the
  2x-EM rule does NOT auto-apply per the strategy spec).

POP is approximated as 1 - |delta_short|. M2M flip price is where the spread
mark first equals the credit collected (P/L = 0). Early-red-P/L score is a
proxy: we shock the underlying by ±0.5 ATR over the first 1-3 days and
estimate how quickly the spread mark exceeds the credit.
"""
from __future__ import annotations

import logging
import math
from datetime import date
from typing import Dict, List, Optional, Sequence, Tuple

from ..config import load_config
from ..data import (
    MarketDataAdapter,
    OptionChain,
    OptionContract,
    black_scholes_greeks,
    get_adapter,
)
from ..scanner import Candidate
from .trade import TradeLeg, TradeProposal

logger = logging.getLogger(__name__)


class TradeBuilder:
    def __init__(self, adapter: Optional[MarketDataAdapter] = None) -> None:
        self.adapter = adapter or get_adapter()
        self.strategy_cfg = load_config("strategy_rules")
        self.failure_cfg = load_config("failure_logic")
        self.data_cfg = load_config("data_config")
        self.rate = float(self.data_cfg.get("risk_free_rate", 0.045))

    # --- public ------------------------------------------------------------

    def build_for_candidate(self, candidate: Candidate) -> List[TradeProposal]:
        proposals: List[TradeProposal] = []
        for exp in candidate.expirations_in_window:
            try:
                chain = self.adapter.get_option_chain(candidate.symbol, exp)
            except Exception as exc:
                logger.warning("chain fetch failed %s @ %s: %s",
                               candidate.symbol, exp, exc)
                continue
            proposals.extend(self._build_from_chain(candidate, chain))

        for p in proposals:
            self._score_proposal(p)
        proposals.sort(key=lambda p: p.rank_score, reverse=True)
        return proposals

    def build_for_candidates(
        self, candidates: Sequence[Candidate], top_n_per: int = 2
    ) -> List[TradeProposal]:
        out: List[TradeProposal] = []
        for c in candidates:
            picks = self.build_for_candidate(c)[:top_n_per]
            out.extend(picks)
        out.sort(key=lambda p: p.rank_score, reverse=True)
        return out

    # --- per-chain construction --------------------------------------------

    def _build_from_chain(
        self, candidate: Candidate, chain: OptionChain
    ) -> List[TradeProposal]:
        spread_cfg = self.strategy_cfg.get("spread", {})
        widths = self._candidate_widths(spread_cfg)
        results: List[TradeProposal] = []

        # Build buffer (in $) — based on expected move for index products,
        # ATR for equities.
        buffer_dollars = self._buffer_dollars(candidate, chain)
        if buffer_dollars <= 0:
            return results

        for w in widths:
            put_spread = self._build_vertical(
                chain, candidate, side="PUT", width=w, buffer_dollars=buffer_dollars
            )
            if put_spread is not None:
                results.append(put_spread)
            call_spread = self._build_vertical(
                chain, candidate, side="CALL", width=w, buffer_dollars=buffer_dollars
            )
            if call_spread is not None:
                results.append(call_spread)

        # Iron condor when both sides exist for the same width.
        for w in widths:
            ic = self._build_iron_condor(
                chain, candidate, width=w, buffer_dollars=buffer_dollars
            )
            if ic is not None:
                results.append(ic)

        return results

    # --- vertical credit spread --------------------------------------------

    def _build_vertical(
        self,
        chain: OptionChain,
        candidate: Candidate,
        side: str,
        width: float,
        buffer_dollars: float,
    ) -> Optional[TradeProposal]:
        spread_cfg = self.strategy_cfg.get("spread", {})
        pop_cfg = self.strategy_cfg.get("pop", {})
        min_ratio = float(spread_cfg.get("min_credit_to_width_ratio", 0.20))
        max_ratio = float(spread_cfg.get("max_credit_to_width_ratio", 0.45))
        pop_min, pop_max = float(pop_cfg.get("min", 0.70)), float(pop_cfg.get("max", 0.90))

        spot = chain.underlying_price
        if side == "PUT":
            strategy = "BULL_PUT"
            target_short = spot - buffer_dollars
            short = self._nearest_contract(chain.puts, target_short, prefer="below")
            if short is None:
                return None
            long = self._nearest_contract(
                chain.puts, short.strike - width, prefer="below"
            )
        else:
            strategy = "BEAR_CALL"
            target_short = spot + buffer_dollars
            short = self._nearest_contract(chain.calls, target_short, prefer="above")
            if short is None:
                return None
            long = self._nearest_contract(
                chain.calls, short.strike + width, prefer="above"
            )

        if long is None or long.strike == short.strike:
            return None

        actual_width = abs(short.strike - long.strike)
        credit = max(0.0, short.mid - long.mid)
        if credit <= 0:
            logger.debug("%s %s w=%.1f rejected: zero credit (short_mid=%.2f, long_mid=%.2f)",
                         candidate.symbol, strategy, width, short.mid, long.mid)
            return None
        ratio = credit / actual_width
        if not (min_ratio <= ratio <= max_ratio):
            logger.debug("%s %s w=%.1f rejected: credit/width %.0f%% outside [%.0f%%, %.0f%%]",
                         candidate.symbol, strategy, width, ratio * 100,
                         min_ratio * 100, max_ratio * 100)
            return None

        pop = self._estimate_pop(short)
        if pop is None or not (pop_min <= pop <= pop_max):
            logger.debug("%s %s w=%.1f rejected: POP %s outside [%.2f, %.2f]",
                         candidate.symbol, strategy, width,
                         f"{pop:.2f}" if pop is not None else "None", pop_min, pop_max)
            return None

        m2m_flip_price = self._m2m_flip_price(chain, short, long, credit, side)
        m2m_dist_pct = abs(m2m_flip_price - spot) / spot if spot > 0 else 0.0
        exp_be_price = self._expiration_breakeven(short, credit, side)
        exp_be_dist_pct = abs(exp_be_price - spot) / spot if spot > 0 else 0.0

        expected_move = self._expected_move(chain, candidate)
        atr = candidate.atr or 0.0
        early_score = self._early_red_pl_score(chain, short, long, credit, side, atr)

        exit_50 = credit * (1 - float(self.strategy_cfg["exits"]["primary_pct"]))
        exit_25 = credit * (1 - float(self.strategy_cfg["exits"]["secondary_pct"]))

        legs = [
            TradeLeg(
                action="SELL", right=short.right, strike=short.strike,
                expiration=chain.expiration, mid=short.mid,
                bid=short.bid, ask=short.ask, delta=short.delta, iv=short.iv,
                contract_symbol=short.contract_symbol,
            ),
            TradeLeg(
                action="BUY", right=long.right, strike=long.strike,
                expiration=chain.expiration, mid=long.mid,
                bid=long.bid, ask=long.ask, delta=long.delta, iv=long.iv,
                contract_symbol=long.contract_symbol,
            ),
        ]

        return TradeProposal(
            symbol=candidate.symbol,
            strategy=strategy,
            expiration=chain.expiration,
            underlying_price=spot,
            legs=legs,
            credit=credit,
            width=actual_width,
            max_loss=actual_width - credit,
            pop=pop,
            m2m_flip_price=m2m_flip_price,
            m2m_flip_distance_pct=m2m_dist_pct,
            expiration_breakeven_price=exp_be_price,
            expiration_breakeven_distance_pct=exp_be_dist_pct,
            expected_move=expected_move,
            atr=atr,
            early_red_pl_score=early_score,
            exit_50pct_target_credit=exit_50,
            exit_25pct_target_credit=exit_25,
            est_days_to_50pct=int(self.strategy_cfg["exits"]["time_target_days_50"]),
            est_days_to_25pct=int(self.strategy_cfg["exits"]["time_target_days_25"]),
            metrics={
                "buffer_dollars": buffer_dollars,
                "short_delta": short.delta,
                "credit_to_width_ratio": ratio,
            },
        )

    # --- iron condor -------------------------------------------------------

    def _build_iron_condor(
        self,
        chain: OptionChain,
        candidate: Candidate,
        width: float,
        buffer_dollars: float,
    ) -> Optional[TradeProposal]:
        put_side = self._build_vertical(chain, candidate, "PUT", width, buffer_dollars)
        call_side = self._build_vertical(chain, candidate, "CALL", width, buffer_dollars)
        if put_side is None or call_side is None:
            return None

        spot = chain.underlying_price
        legs = put_side.legs + call_side.legs
        credit = put_side.credit + call_side.credit
        # Only one side can lose at expiration -> max loss is widest wing - total credit.
        max_loss = max(put_side.width, call_side.width) - credit
        if max_loss <= 0:
            return None

        flip_low = put_side.m2m_flip_price
        flip_high = call_side.m2m_flip_price
        nearer_flip = flip_low if abs(flip_low - spot) < abs(flip_high - spot) else flip_high
        nearer_flip_dist = min(abs(flip_low - spot), abs(flip_high - spot)) / spot

        # Expiration breakevens — also take the nearer side.
        be_low = put_side.expiration_breakeven_price
        be_high = call_side.expiration_breakeven_price
        nearer_be = be_low if abs(be_low - spot) < abs(be_high - spot) else be_high
        nearer_be_dist = min(abs(be_low - spot), abs(be_high - spot)) / spot

        # Joint POP ≈ product of side POPs (independence approximation).
        pop = put_side.pop * call_side.pop
        atr = candidate.atr or 0.0
        early_score = min(put_side.early_red_pl_score, call_side.early_red_pl_score)

        exit_50 = credit * (1 - float(self.strategy_cfg["exits"]["primary_pct"]))
        exit_25 = credit * (1 - float(self.strategy_cfg["exits"]["secondary_pct"]))

        return TradeProposal(
            symbol=candidate.symbol,
            strategy="IRON_CONDOR",
            expiration=chain.expiration,
            underlying_price=spot,
            legs=legs,
            credit=credit,
            width=max(put_side.width, call_side.width),
            max_loss=max_loss,
            pop=pop,
            m2m_flip_price=nearer_flip,
            m2m_flip_distance_pct=nearer_flip_dist,
            expiration_breakeven_price=nearer_be,
            expiration_breakeven_distance_pct=nearer_be_dist,
            expected_move=put_side.expected_move,
            atr=atr,
            early_red_pl_score=early_score,
            exit_50pct_target_credit=exit_50,
            exit_25pct_target_credit=exit_25,
            est_days_to_50pct=int(self.strategy_cfg["exits"]["time_target_days_50"]),
            est_days_to_25pct=int(self.strategy_cfg["exits"]["time_target_days_25"]),
            metrics={
                "put_flip": flip_low, "call_flip": flip_high,
                "buffer_dollars": buffer_dollars,
            },
        )

    # --- analytics ---------------------------------------------------------

    def _candidate_widths(self, spread_cfg: Dict) -> List[float]:
        wmin = float(spread_cfg.get("min_width", 1.0))
        wmax = float(spread_cfg.get("max_width", 5.0))
        pref = float(spread_cfg.get("preferred_width", 2.5))
        # A handful of widths to try; preferred listed first.
        widths = sorted({pref, wmin, wmax, (wmin + pref) / 2.0, (pref + wmax) / 2.0})
        return [w for w in widths if wmin <= w <= wmax]

    def _buffer_dollars(self, candidate: Candidate, chain: OptionChain) -> float:
        bcfg = self.strategy_cfg.get("buffers", {})
        if candidate.is_index_product:
            em = self._expected_move(chain, candidate)
            mult = self._index_em_multiplier(bcfg)
            return em * mult
        atr = candidate.atr or 0.0
        return atr * float(bcfg.get("equity_atr_multiplier", 1.5))

    def _index_em_multiplier(self, bcfg: Dict) -> float:
        """Look up the VIX-aware index EM multiplier.

        Tiers are evaluated in declared order. The first tier whose
        `vix_max` is >= current VIX (or null = catch-all) wins. Falls back
        to the legacy single `index_em_multiplier` if no tiers present.
        """
        tiers = bcfg.get("index_em_tiers")
        if not tiers:
            return float(bcfg.get("index_em_multiplier", 2.0))
        try:
            vix = float(self.adapter.get_vix().last)
        except Exception:
            return float(bcfg.get("index_em_multiplier", 2.0))
        for tier in tiers:
            vmax = tier.get("vix_max")
            if vmax is None or vix <= float(vmax):
                return float(tier.get("em_multiplier", 2.0))
        return float(bcfg.get("index_em_multiplier", 2.0))

    def _expected_move(self, chain: OptionChain, candidate: Candidate) -> float:
        """1-sigma expected move to expiration: S * IV * sqrt(t)."""
        t_years = max((chain.expiration - date.today()).days, 0) / 365.0
        iv = candidate.avg_iv
        return chain.underlying_price * iv * math.sqrt(t_years)

    @staticmethod
    def _nearest_contract(
        contracts: List[OptionContract], target: float, prefer: str
    ) -> Optional[OptionContract]:
        """`prefer='below'` returns the highest strike <= target; `'above'` the
        lowest >= target. Falls back to nearest if no side matches."""
        usable = [c for c in contracts if c.bid >= 0 and c.ask > 0]
        if not usable:
            return None
        if prefer == "below":
            below = [c for c in usable if c.strike <= target]
            if below:
                return max(below, key=lambda c: c.strike)
        elif prefer == "above":
            above = [c for c in usable if c.strike >= target]
            if above:
                return min(above, key=lambda c: c.strike)
        return min(usable, key=lambda c: abs(c.strike - target))

    @staticmethod
    def _estimate_pop(short: OptionContract) -> Optional[float]:
        if short.delta is None:
            return None
        # POP for OTM short ≈ 1 - |delta|.
        return max(0.0, min(1.0, 1.0 - abs(short.delta)))

    def _spread_value(
        self,
        spot: float,
        short: OptionContract,
        long: OptionContract,
        side: str,
        days_forward: int = 0,
        iv_shock: float = 0.0,
    ) -> float:
        """Estimated value of the spread at a given underlying price.

        We re-price both legs with Black-Scholes at the current IV, with time
        decremented by `days_forward` calendar days. `iv_shock` is an additive
        bump applied to both legs' IV — e.g., 0.05 means "vol +5 pts." Used
        for M2M flip, early-red scenarios, and vol-expansion stress.
        """
        days_to_exp = max((short.expiration - date.today()).days - days_forward, 0)
        t_years = days_to_exp / 365.0
        iv_s = max((short.iv or 0.30) + iv_shock, 0.01)
        iv_l = max((long.iv or short.iv or 0.30) + iv_shock, 0.01)
        right = short.right

        short_price = black_scholes_greeks(
            spot, short.strike, t_years, self.rate, iv_s, right
        ).price
        long_price = black_scholes_greeks(
            spot, long.strike, t_years, self.rate, iv_l, right
        ).price
        return short_price - long_price

    def _expiration_breakeven(
        self, short: OptionContract, credit: float, side: str
    ) -> float:
        """Closed-form breakeven AT EXPIRATION: short ± credit. Useful as a
        secondary reference but does NOT capture early-red behavior."""
        return short.strike - credit if side == "PUT" else short.strike + credit

    def _m2m_flip_price(
        self,
        chain: OptionChain,
        short: OptionContract,
        long: OptionContract,
        credit: float,
        side: str,
    ) -> float:
        """Early-red M2M flip — the *path-aware* risk threshold.

        Definition: the underlying price level at which, `days_forward` days
        from entry (default 5), the spread's M2M loss equals
        `early_red_loss_pct` of credit (default 25%). This captures how the
        trade actually behaves in the days *after* entry, not where it goes
        red at expiration. It's the number a live risk manager wants:
        "how far against me can the underlying move in the first week before
        I'm meaningfully underwater on M2M?"

        Algorithm: at days_forward, theta has erased some premium, so the
        spread mark at spot is lower than the entry credit. The adverse
        price level where mark = credit * (1 + early_red_loss_pct) is found
        by bisection between spot and short.strike (BULL_PUT) or spot and
        2*short.strike (BEAR_CALL).
        """
        m2m_cfg = self.strategy_cfg.get("m2m", {}) or {}
        days_forward = int(m2m_cfg.get("early_red_days_forward", 5))
        loss_pct = float(m2m_cfg.get("early_red_loss_pct", 0.25))
        target_value = credit * (1.0 + loss_pct)

        spot = chain.underlying_price
        if side == "PUT":
            # Adverse = price drops. Search [short.strike, spot] (mark
            # increases as we drop through the short).
            lo, hi = short.strike * 0.5, spot
        else:
            # Adverse = price rises. Search [spot, short.strike * 1.5].
            lo, hi = spot, short.strike * 1.5

        def f(s: float) -> float:
            return self._spread_value(s, short, long, side,
                                      days_forward=days_forward) - target_value

        f_lo, f_hi = f(lo), f(hi)
        # Bracket check. If both endpoints are below the target, the trade
        # never reaches `loss_pct` adverse in the window — return the
        # closest-to-target endpoint as a conservative answer.
        if f_lo * f_hi > 0:
            # Same sign — no crossing. Pick whichever endpoint is closer to
            # the target value as a sentinel.
            return lo if abs(f_lo) < abs(f_hi) else hi

        for _ in range(60):
            mid = (lo + hi) / 2.0
            f_mid = f(mid)
            if abs(f_mid) < 1e-4:
                return mid
            if f_lo * f_mid < 0:
                hi, f_hi = mid, f_mid
            else:
                lo, f_lo = mid, f_mid
        return (lo + hi) / 2.0

    def _early_red_pl_score(
        self,
        chain: OptionChain,
        short: OptionContract,
        long: OptionContract,
        credit: float,
        side: str,
        atr: float,
    ) -> float:
        """Score in [0, 1]; higher = more resilient.

        Combines spot shocks AND IV shocks across days 1-5. Each scenario
        re-prices the spread under stress; "green" means the mark is still
        below entry credit (no M2M loss). The score is the fraction of
        green scenarios.

        This is the second-generation resilience score — earlier versions
        only tested linear spot moves at flat IV, which Chat correctly
        flagged as missing vol expansion. Still an approximation (no
        momentum continuation, no path correlation), but materially better
        than a single ATR-shock pass.
        """
        if atr <= 0:
            return 0.5
        spot = chain.underlying_price
        adverse_dir = -1.0 if side == "PUT" else 1.0
        scenarios: List[bool] = []
        # Spot shocks (atr-multiple) crossed with IV shocks (vol pts added)
        # over days 1..5. 4 spot levels × 3 iv levels × 5 days = 60 scenarios.
        for days in (1, 2, 3, 4, 5):
            for spot_mult in (0.25, 0.5, 0.75, 1.0):
                shocked_spot = spot + adverse_dir * spot_mult * atr
                for iv_shock in (0.0, 0.05, 0.10):
                    val = self._spread_value(
                        shocked_spot, short, long, side,
                        days_forward=days, iv_shock=iv_shock,
                    )
                    scenarios.append(val <= credit)
        return sum(scenarios) / len(scenarios) if scenarios else 0.5

    # --- ranking ------------------------------------------------------------

    def _score_proposal(self, p: TradeProposal) -> None:
        weights = self.strategy_cfg.get("ranking_weights", {})
        target_pop = float(self.strategy_cfg.get("pop", {}).get("target", 0.80))

        # POP centering: peaks at target_pop.
        pop_score = 1.0 - abs(p.pop - target_pop) / 0.20
        pop_score = max(0.0, min(1.0, pop_score))

        # M2M distance: more is better, scaled vs expected move.
        em_ref = max(p.expected_move, 1e-6)
        m2m_dollars = abs(p.m2m_flip_price - p.underlying_price)
        m2m_score = min(m2m_dollars / (1.5 * em_ref), 1.5) / 1.5
        m2m_score = max(0.0, min(1.0, m2m_score))

        # Credit/width sweet spot: 0.30 ratio = 1.0, decays away.
        ratio = p.credit_to_width_ratio
        credit_score = max(0.0, 1.0 - abs(ratio - 0.30) / 0.30)

        # Liquidity proxy: average leg spread quality.
        spread_pcts = []
        for leg in p.legs:
            mid = leg.mid if leg.mid > 0 else (leg.bid + leg.ask) / 2.0
            if mid > 0:
                spread_pcts.append((leg.ask - leg.bid) / mid)
        avg_spread = sum(spread_pcts) / len(spread_pcts) if spread_pcts else 0.5
        liquidity_score = max(0.0, 1.0 - avg_spread / 0.10)

        # Early-red P/L resilience.
        red_score = p.early_red_pl_score

        # Failure-logic penalties.
        m2m_cfg = self.failure_cfg.get("m2m", {})
        penalty = 0.0
        reject_pct = float(m2m_cfg.get("reject_pct_distance", 0.015))
        warn_pct = float(m2m_cfg.get("warn_pct_distance", 0.03))
        penalty_pct = float(m2m_cfg.get("penalty_band_pct", 0.05))
        if p.m2m_flip_distance_pct < reject_pct:
            p.flags.append("M2M_TOO_CLOSE")
            penalty += 1.0
        elif p.m2m_flip_distance_pct < warn_pct:
            p.flags.append("M2M_WARN")
            penalty += 0.4
        elif p.m2m_flip_distance_pct < penalty_pct:
            penalty += 0.15

        if red_score < 0.4:
            p.flags.append("EARLY_RED_VULNERABLE")
            penalty += 0.3

        score = (
            float(weights.get("pop_centering", 1.0)) * pop_score
            + float(weights.get("m2m_distance", 1.5)) * m2m_score
            + float(weights.get("credit_quality", 1.0)) * credit_score
            + float(weights.get("liquidity", 0.8)) * liquidity_score
            + float(weights.get("early_red_pl_penalty", 1.2)) * red_score
        ) - penalty

        p.rank_score = score
        p.rank_reasons = [
            f"pop_score={pop_score:.2f}",
            f"m2m_score={m2m_score:.2f}",
            f"credit_score={credit_score:.2f}",
            f"liquidity_score={liquidity_score:.2f}",
            f"early_red_score={red_score:.2f}",
            f"penalty={penalty:.2f}",
        ]
