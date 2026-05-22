"""Real-time validator.

Trade construction can happen seconds or minutes before manual entry — the
market moves in that gap. This module re-fetches a fresh chain for the
proposal's expiration (cache TTL is short for chains, so a refetch is
typically a real call) and confirms:

- Regime is still DEPLOY.
- The short leg's quoted bid/ask still produces a credit within tolerance.
- Bid/ask spread is still within liquidity bounds.
- M2M flip distance is still above the failure-logic reject threshold.
- IV hasn't blown out beyond the scanner's max.

Output: a ValidationResult marked VALID or INVALID with a list of reasons
that can be rendered straight to the user.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Optional

from ..config import load_config
from ..data import MarketDataAdapter, OptionChain, OptionContract, get_adapter
from ..regime_engine import RegimeEngine, RegimeReading
from ..trade_builder import TradeProposal


@dataclass
class ValidationResult:
    proposal: TradeProposal
    valid: bool
    reasons: List[str] = field(default_factory=list)
    fresh_credit: Optional[float] = None
    credit_drift_pct: Optional[float] = None
    regime: Optional[RegimeReading] = None
    flags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.proposal.symbol,
            "strategy": self.proposal.strategy,
            "expiration": self.proposal.expiration.isoformat(),
            "valid": self.valid,
            "reasons": list(self.reasons),
            "fresh_credit": self.fresh_credit,
            "credit_drift_pct": self.credit_drift_pct,
            "regime": self.regime.to_dict() if self.regime else None,
            "flags": list(self.flags),
        }


class Validator:
    # Max acceptable change in credit between build-time and entry-time.
    DEFAULT_CREDIT_DRIFT = 0.15

    def __init__(
        self,
        adapter: Optional[MarketDataAdapter] = None,
        regime_engine: Optional[RegimeEngine] = None,
    ) -> None:
        self.adapter = adapter or get_adapter()
        self.regime_engine = regime_engine or RegimeEngine(self.adapter)
        self.scanner_cfg = load_config("scanner_config")
        self.failure_cfg = load_config("failure_logic")

    def validate(self, proposal: TradeProposal) -> ValidationResult:
        reasons: List[str] = []
        flags: List[str] = []

        # 1. Regime gate.
        regime = self.regime_engine.evaluate()
        if not regime.deploy:
            reasons.append(f"regime gate closed: {regime.regime}")
            return ValidationResult(
                proposal=proposal, valid=False, reasons=reasons, regime=regime,
            )

        # 2. Re-fetch the chain.
        try:
            fresh = self.adapter.get_option_chain(proposal.symbol, proposal.expiration)
        except Exception as exc:
            reasons.append(f"failed to refetch chain: {exc}")
            return ValidationResult(
                proposal=proposal, valid=False, reasons=reasons, regime=regime,
            )

        # 3. Resolve contracts in the fresh chain.
        leg_contracts: List[OptionContract] = []
        for leg in proposal.legs:
            pool = fresh.calls if leg.right.upper().startswith("C") else fresh.puts
            match = next((c for c in pool if abs(c.strike - leg.strike) < 1e-6), None)
            if match is None:
                reasons.append(f"missing leg in fresh chain: {leg.right} {leg.strike}")
                return ValidationResult(
                    proposal=proposal, valid=False, reasons=reasons, regime=regime,
                )
            leg_contracts.append(match)

        # 4. Recompute credit from fresh quotes.
        fresh_credit = 0.0
        for leg, contract in zip(proposal.legs, leg_contracts):
            sign = 1.0 if leg.action == "SELL" else -1.0
            fresh_credit += sign * contract.mid

        if fresh_credit <= 0:
            reasons.append(f"fresh credit non-positive: {fresh_credit:.3f}")
            return ValidationResult(
                proposal=proposal, valid=False, reasons=reasons,
                fresh_credit=fresh_credit, regime=regime,
            )

        # 5. Credit drift.
        drift = (
            (fresh_credit - proposal.credit) / proposal.credit
            if proposal.credit > 0 else 0.0
        )
        if abs(drift) > self.DEFAULT_CREDIT_DRIFT:
            reasons.append(
                f"credit drift {drift:+.1%} exceeds {self.DEFAULT_CREDIT_DRIFT:+.0%}"
            )
            return ValidationResult(
                proposal=proposal, valid=False, reasons=reasons,
                fresh_credit=fresh_credit, credit_drift_pct=drift, regime=regime,
            )

        # 6. Liquidity check on fresh quotes.
        max_spread = float(self.scanner_cfg.get("liquidity", {})
                           .get("max_bid_ask_spread_pct", 0.10))
        for contract in leg_contracts:
            if contract.spread_pct > max_spread:
                flags.append(
                    f"wide spread on {contract.right} {contract.strike}: "
                    f"{contract.spread_pct:.1%}"
                )

        # 7. IV ceiling check (a fresh IV blowout could mean an event we missed).
        iv_max = float(self.scanner_cfg.get("iv", {}).get("max", 0.80))
        ivs = [c.iv for c in leg_contracts if c.iv]
        if ivs and max(ivs) > iv_max:
            reasons.append(f"IV blew out: max leg IV {max(ivs):.0%} > cap {iv_max:.0%}")
            return ValidationResult(
                proposal=proposal, valid=False, reasons=reasons,
                fresh_credit=fresh_credit, credit_drift_pct=drift, regime=regime, flags=flags,
            )

        # 8. Early-red M2M flip proximity vs current spot. With the path-aware
        # definition, the flip is materially closer to spot than the old
        # expiration-breakeven measure, so the reject threshold lives under
        # `m2m.early_red_reject_pct_distance` (separate config) and falls
        # back to the legacy `m2m.reject_pct_distance` if not set.
        spot = fresh.underlying_price
        m2m_dist_pct = abs(proposal.m2m_flip_price - spot) / spot if spot > 0 else 0.0
        m2m_cfg = self.failure_cfg.get("m2m", {})
        reject_pct = float(
            m2m_cfg.get("early_red_reject_pct_distance",
                        m2m_cfg.get("reject_pct_distance", 0.015))
        )
        if m2m_dist_pct < reject_pct:
            reasons.append(
                f"Early-red M2M flip too close: {m2m_dist_pct:.2%} < {reject_pct:.2%}"
            )
            return ValidationResult(
                proposal=proposal, valid=False, reasons=reasons,
                fresh_credit=fresh_credit, credit_drift_pct=drift, regime=regime, flags=flags,
            )

        # 9. Gamma window.
        days_to_exp = (proposal.expiration - date.today()).days
        no_open = int(self.failure_cfg.get("gamma", {}).get("no_open_dte", 5))
        if days_to_exp <= no_open:
            reasons.append(f"too close to expiry: {days_to_exp} DTE <= {no_open}")
            return ValidationResult(
                proposal=proposal, valid=False, reasons=reasons,
                fresh_credit=fresh_credit, credit_drift_pct=drift, regime=regime, flags=flags,
            )

        return ValidationResult(
            proposal=proposal, valid=True,
            reasons=["all checks passed"],
            fresh_credit=fresh_credit, credit_drift_pct=drift,
            regime=regime, flags=flags,
        )
