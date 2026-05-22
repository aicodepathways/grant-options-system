"""Backtest engine.

Walks forward day-by-day:
  1. Set the BacktestAdapter's as-of date.
  2. Run regime check; skip if NO-TRADE.
  3. Run scanner → builder → validator (same code as live).
  4. For each VALID proposal, simulate the trade by re-pricing the spread
     each subsequent day until either (a) a profit-target trip, (b) a
     failure-logic exit, or (c) expiration.

Outputs: per-trade outcomes plus aggregate metrics (win rate, avg P/L,
max drawdown, regime breakdown). All synthetic-chain caveats apply.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any, Dict, List, Optional

import pandas as pd

from ..data import OptionChain, black_scholes_greeks
from ..failure_logic import (
    PositionState,
    evaluate_open_position,
)
from ..regime_engine import RegimeEngine, RegimeReading
from ..scanner import Scanner
from ..trade_builder import TradeBuilder, TradeProposal
from ..validator import Validator
from .synthetic_chains import BacktestAdapter

logger = logging.getLogger(__name__)


@dataclass
class TradeOutcome:
    proposal: TradeProposal
    entry_date: date
    exit_date: date
    exit_reason: str
    entry_credit: float
    exit_debit: float
    pnl_per_spread: float
    days_held: int
    regime_at_entry: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.proposal.symbol,
            "strategy": self.proposal.strategy,
            "entry_date": self.entry_date.isoformat(),
            "exit_date": self.exit_date.isoformat(),
            "exit_reason": self.exit_reason,
            "entry_credit": self.entry_credit,
            "exit_debit": self.exit_debit,
            "pnl_per_spread": self.pnl_per_spread,
            "days_held": self.days_held,
            "regime_at_entry": self.regime_at_entry,
            "expiration": self.proposal.expiration.isoformat(),
        }


@dataclass
class BacktestResult:
    outcomes: List[TradeOutcome] = field(default_factory=list)
    daily_regimes: List[Dict[str, Any]] = field(default_factory=list)
    approximation_warning: str = (
        "Synthetic option chains used — IVs are realized-vol proxies, "
        "skew is ignored. Treat absolute returns as indicative only."
    )

    def metrics(self) -> Dict[str, Any]:
        if not self.outcomes:
            return {"trades": 0, "warning": self.approximation_warning}
        pnls = [o.pnl_per_spread for o in self.outcomes]
        wins = [p for p in pnls if p > 0]
        losses = [p for p in pnls if p <= 0]
        total = sum(pnls)
        equity = []
        running = 0.0
        for p in pnls:
            running += p
            equity.append(running)
        peak = -float("inf")
        max_dd = 0.0
        for x in equity:
            peak = max(peak, x)
            max_dd = min(max_dd, x - peak)

        by_regime: Dict[str, List[float]] = {}
        for o in self.outcomes:
            by_regime.setdefault(o.regime_at_entry, []).append(o.pnl_per_spread)
        regime_breakdown = {
            r: {
                "trades": len(v),
                "win_rate": sum(1 for x in v if x > 0) / len(v),
                "avg_pnl": sum(v) / len(v),
            } for r, v in by_regime.items()
        }
        return {
            "trades": len(self.outcomes),
            "wins": len(wins),
            "losses": len(losses),
            "win_rate": len(wins) / len(self.outcomes),
            "avg_pnl_per_spread": total / len(self.outcomes),
            "total_pnl_per_spread": total,
            "best_trade": max(pnls),
            "worst_trade": min(pnls),
            "max_drawdown_per_spread": max_dd,
            "by_regime": regime_breakdown,
            "warning": self.approximation_warning,
        }


class Backtester:
    def __init__(self, adapter: Optional[BacktestAdapter] = None) -> None:
        self.adapter = adapter or BacktestAdapter()
        self.scanner = Scanner(self.adapter)
        self.builder = TradeBuilder(self.adapter)
        self.validator = Validator(self.adapter)
        self.regime_engine = RegimeEngine(self.adapter)

    def run(
        self,
        start: date,
        end: date,
        max_concurrent: int = 5,
        scan_every_n_days: int = 1,
    ) -> BacktestResult:
        """Walk start..end inclusive, taking trades subject to a concurrency cap."""
        result = BacktestResult()
        open_positions: List[TradeOutcome] = []
        symbol_history_cache: Dict[str, pd.DataFrame] = {}

        cur = start
        scan_counter = 0
        while cur <= end:
            self.adapter.set_as_of(cur)

            # 1. Manage open positions.
            still_open: List[TradeOutcome] = []
            for trade in open_positions:
                outcome = self._step_position(trade, cur, symbol_history_cache)
                if outcome is None:
                    still_open.append(trade)
                else:
                    result.outcomes.append(outcome)
            open_positions = still_open

            # 2. Regime + new entries.
            try:
                regime = self.regime_engine.evaluate()
            except Exception as exc:
                logger.warning("regime evaluate failed @ %s: %s", cur, exc)
                cur += timedelta(days=1)
                continue
            result.daily_regimes.append({"date": cur.isoformat(), **regime.to_dict()})

            scan_counter += 1
            if (regime.deploy
                    and len(open_positions) < max_concurrent
                    and scan_counter % scan_every_n_days == 0):
                self._open_new_trades(cur, regime, open_positions, max_concurrent, result)

            cur += timedelta(days=1)

        # Force-close anything still open at end-of-window.
        for trade in open_positions:
            forced = self._force_close(trade, end, symbol_history_cache)
            if forced is not None:
                result.outcomes.append(forced)

        return result

    # --- helpers ------------------------------------------------------------

    def _open_new_trades(
        self,
        as_of: date,
        regime: RegimeReading,
        open_positions: List[TradeOutcome],
        max_concurrent: int,
        result: BacktestResult,
    ) -> None:
        try:
            candidates = self.scanner.scan()
        except Exception as exc:
            logger.warning("scan failed @ %s: %s", as_of, exc)
            return

        proposals = self.builder.build_for_candidates(candidates, top_n_per=1)
        slots = max_concurrent - len(open_positions)
        for proposal in proposals[:slots]:
            try:
                v = self.validator.validate(proposal)
            except Exception as exc:
                logger.warning("validate failed: %s", exc)
                continue
            if not v.valid:
                continue
            outcome = TradeOutcome(
                proposal=proposal,
                entry_date=as_of,
                exit_date=as_of,             # placeholder, overwritten on close
                exit_reason="OPEN",
                entry_credit=v.fresh_credit or proposal.credit,
                exit_debit=0.0,
                pnl_per_spread=0.0,
                days_held=0,
                regime_at_entry=regime.regime,
            )
            open_positions.append(outcome)

    def _spread_mark(
        self, proposal: TradeProposal, as_of: date, underlying: float
    ) -> float:
        """Re-price the spread on `as_of` with realized-vol proxy as IV."""
        days_to_exp = max((proposal.expiration - as_of).days, 0)
        if days_to_exp == 0:
            # Intrinsic only at expiry.
            value = 0.0
            for leg in proposal.legs:
                sign = -1.0 if leg.action == "SELL" else 1.0
                if leg.right.upper().startswith("C"):
                    intrinsic = max(0.0, underlying - leg.strike)
                else:
                    intrinsic = max(0.0, leg.strike - underlying)
                value += sign * intrinsic
            # Mark-to-close means we PAY this much to flatten. Convention: positive = debit.
            return -value
        t = days_to_exp / 365.0
        rate = self.builder.rate
        debit = 0.0
        for leg in proposal.legs:
            iv = leg.iv or 0.25
            g = black_scholes_greeks(
                underlying, leg.strike, t, rate, iv, leg.right
            )
            sign = 1.0 if leg.action == "SELL" else -1.0
            debit += sign * g.price
        return max(debit, 0.0)

    def _step_position(
        self,
        trade: TradeOutcome,
        as_of: date,
        cache: Dict[str, pd.DataFrame],
    ) -> Optional[TradeOutcome]:
        sym = trade.proposal.symbol
        if sym not in cache:
            cache[sym] = self.adapter._full_history(sym)
        hist = cache[sym]
        bar = hist[hist.index <= pd.Timestamp(as_of)]
        if bar.empty:
            return None
        underlying = float(bar["close"].iloc[-1])
        mark = self._spread_mark(trade.proposal, as_of, underlying)
        days_held = (as_of - trade.entry_date).days

        state = PositionState(
            proposal=trade.proposal,
            current_underlying=underlying,
            current_spread_mark=mark,
            days_held=days_held,
        )
        signals = evaluate_open_position(state)

        # Any EXIT signal closes the trade.
        for sig in signals:
            if sig.severity == "EXIT":
                return self._close(trade, as_of, mark, sig.code)

        # Hard time stop at 10 DTE.
        if (trade.proposal.expiration - as_of).days <= 10:
            return self._close(trade, as_of, mark, "TIME_STOP_10_DTE")

        # Expiration arrival.
        if as_of >= trade.proposal.expiration:
            return self._close(trade, as_of, mark, "EXPIRED")

        return None

    def _force_close(
        self, trade: TradeOutcome, as_of: date, cache: Dict[str, pd.DataFrame]
    ) -> Optional[TradeOutcome]:
        sym = trade.proposal.symbol
        if sym not in cache:
            cache[sym] = self.adapter._full_history(sym)
        hist = cache[sym]
        bar = hist[hist.index <= pd.Timestamp(as_of)]
        if bar.empty:
            return None
        underlying = float(bar["close"].iloc[-1])
        mark = self._spread_mark(trade.proposal, as_of, underlying)
        return self._close(trade, as_of, mark, "BACKTEST_END")

    @staticmethod
    def _close(trade: TradeOutcome, as_of: date,
               mark: float, reason: str) -> TradeOutcome:
        trade.exit_date = as_of
        trade.exit_debit = mark
        trade.pnl_per_spread = trade.entry_credit - mark
        trade.days_held = (as_of - trade.entry_date).days
        trade.exit_reason = reason
        return trade
