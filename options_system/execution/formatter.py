"""Robinhood-compatible trade-instruction formatter.

Robinhood's mobile UI requires manual leg entry — there's no API. We render
a compact, mobile-readable card that maps directly to RH's order ticket:
- per-leg side / strike / expiration / right
- suggested limit price (slightly inside mid for fill probability)
- trade-management levels for the user's reference
"""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional

from ..trade_builder import TradeProposal
from ..validator import ValidationResult


def suggested_limit_price(proposal: TradeProposal,
                          aggressiveness: float = 0.30) -> float:
    """Limit price for a credit spread.

    `aggressiveness` is in [0, 1]. 0 = at mid (best price, low fill odds),
    1 = at the natural (sum of bids on the short legs minus sum of asks on
    the long legs). 0.30 — slightly inside mid — is a reasonable default.
    """
    natural = 0.0
    mid = 0.0
    for leg in proposal.legs:
        sign = 1.0 if leg.action == "SELL" else -1.0
        leg_mid = leg.mid if leg.mid > 0 else (leg.bid + leg.ask) / 2.0
        mid += sign * leg_mid
        if leg.action == "SELL":
            natural += leg.bid     # sell at bid -> immediate fill
        else:
            natural -= leg.ask     # buy at ask -> immediate fill
    aggressiveness = max(0.0, min(1.0, aggressiveness))
    limit = mid + aggressiveness * (natural - mid)
    return round(max(limit, 0.01), 2)


def _fmt_date(d: date) -> str:
    return d.strftime("%b %d, %Y")


def format_trade_card(
    proposal: TradeProposal,
    validation: Optional[ValidationResult] = None,
    contracts: int = 1,
) -> str:
    """Plain-text trade card. Designed to read cleanly in a chat / mobile."""
    lines: List[str] = []
    lines.append("=" * 56)
    lines.append(f"  {proposal.strategy}  —  {proposal.symbol}  "
                 f"(spot ${proposal.underlying_price:.2f})")
    lines.append(f"  Expires: {_fmt_date(proposal.expiration)}   "
                 f"DTE: {(proposal.expiration - date.today()).days}")
    lines.append("=" * 56)
    lines.append("")
    lines.append("LEGS  (Robinhood: Trade > Trade Options > custom)")
    for i, leg in enumerate(proposal.legs, 1):
        right_word = "Call" if leg.right.upper().startswith("C") else "Put"
        lines.append(f"  {i}. {leg.action:<4} {right_word:<4} "
                     f"${leg.strike:>7.2f}  exp {_fmt_date(leg.expiration)}  "
                     f"({leg.contract_symbol or '—'})")
        lines.append(f"       bid {leg.bid:.2f} / ask {leg.ask:.2f} / mid {leg.mid:.2f}"
                     + (f"   delta {leg.delta:+.2f}" if leg.delta is not None else ""))
    lines.append("")

    fresh_credit = (validation.fresh_credit if (validation and validation.fresh_credit) else proposal.credit)
    limit = suggested_limit_price(proposal)

    lines.append("ORDER")
    lines.append(f"  Type:           Net Credit")
    lines.append(f"  Quantity:       {contracts} spread{'s' if contracts != 1 else ''}")
    lines.append(f"  Limit Price:    ${limit:.2f}    (mid-credit, work toward natural)")
    lines.append(f"  Credit Target:  ${fresh_credit:.2f}")
    lines.append(f"  Width:          ${proposal.width:.2f}     "
                 f"Max Loss: ${proposal.max_loss:.2f}")
    lines.append(f"  POP:            {proposal.pop:.0%}        "
                 f"Credit/Width: {proposal.credit_to_width_ratio:.0%}")
    lines.append("")

    lines.append("RISK")
    er_dir = ("below" if proposal.m2m_flip_price < proposal.underlying_price
              else "above")
    be_dir = ("below" if proposal.expiration_breakeven_price < proposal.underlying_price
              else "above")
    lines.append(f"  Early-red M2M flip:  ${proposal.m2m_flip_price:.2f}    "
                 f"({proposal.m2m_flip_distance_pct:.2%} {er_dir} spot, "
                 f"path-aware 5d / 25% credit loss)")
    lines.append(f"  Expiration breakeven: ${proposal.expiration_breakeven_price:.2f}    "
                 f"({proposal.expiration_breakeven_distance_pct:.2%} {be_dir} spot)")
    lines.append(f"  Expected move:     ${proposal.expected_move:.2f}     "
                 f"ATR: ${proposal.atr:.2f}")
    lines.append(f"  Resilience score:  {proposal.early_red_pl_score:.2f}    "
                 f"(higher = more resilient; spot + IV shocks over 5d)")
    if proposal.flags:
        lines.append(f"  Flags:             {', '.join(proposal.flags)}")
    lines.append("")

    lines.append("MANAGEMENT")
    lines.append(f"  Take 50% off at:   buy back at ${proposal.exit_50pct_target_credit:.2f}  "
                 f"(~{proposal.est_days_to_50pct}d)")
    lines.append(f"  Scale 25% off at:  buy back at ${proposal.exit_25pct_target_credit:.2f}  "
                 f"(~{proposal.est_days_to_25pct}d)")
    lines.append(f"  Hard stop:         M2M flip breached, or loss exceeds 2x credit")
    lines.append(f"  Time stop:         close by 10 DTE regardless of P/L")

    if validation is not None:
        lines.append("")
        lines.append("VALIDATION")
        status = "VALID — OK to enter" if validation.valid else "INVALID — DO NOT ENTER"
        lines.append(f"  Status:  {status}")
        for r in validation.reasons:
            lines.append(f"    - {r}")
        if validation.flags:
            lines.append(f"  Warnings (non-blocking):")
            for f in validation.flags:
                lines.append(f"    - {f}")
        if validation.credit_drift_pct is not None:
            lines.append(f"  Credit drift since build: {validation.credit_drift_pct:+.1%}")
        if validation.regime is not None:
            lines.append(f"  Regime: {validation.regime.regime} "
                         f"(deploy={validation.regime.deploy})")

    lines.append("=" * 56)
    return "\n".join(lines)


def format_trade_card_dict(
    proposal: TradeProposal,
    validation: Optional[ValidationResult] = None,
    contracts: int = 1,
) -> Dict[str, Any]:
    """Structured equivalent of `format_trade_card`. Useful for the log."""
    return {
        "rendered": format_trade_card(proposal, validation, contracts),
        "proposal": proposal.to_dict(),
        "validation": validation.to_dict() if validation else None,
        "contracts": contracts,
        "suggested_limit": suggested_limit_price(proposal),
    }
