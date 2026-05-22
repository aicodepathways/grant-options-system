"""Failure-logic rules.

All thresholds come from `failure_logic.yaml`. The functions here are pure —
no I/O — so they can be reused from the validator, the daily orchestrator,
and the backtester without coupling to a data adapter.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Optional

from ..config import load_config
from ..trade_builder import TradeProposal


@dataclass
class FailureSignal:
    code: str            # e.g. 'M2M_TOO_CLOSE', 'GAMMA_HOT'
    severity: str        # 'INFO' | 'WARN' | 'REJECT' | 'EXIT'
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return {"code": self.code, "severity": self.severity, "message": self.message}


@dataclass
class PositionState:
    proposal: TradeProposal
    current_underlying: float
    current_spread_mark: float    # current debit to close
    days_held: int = 0

    @property
    def days_to_expiration(self) -> int:
        return max((self.proposal.expiration - date.today()).days, 0)

    @property
    def unrealized_pl_per_spread(self) -> float:
        # Sold for `credit`, can buy back for `current_spread_mark`.
        return self.proposal.credit - self.current_spread_mark


# --- pre-trade evaluation ---------------------------------------------------


def evaluate_proposal(proposal: TradeProposal,
                      cfg: Optional[Dict[str, Any]] = None) -> List[FailureSignal]:
    """Hard checks that should reject a proposal at entry."""
    cfg = cfg or load_config("failure_logic")
    signals: List[FailureSignal] = []

    # M2M proximity.
    m2m_cfg = cfg.get("m2m", {})
    reject_pct = float(m2m_cfg.get("reject_pct_distance", 0.015))
    warn_pct = float(m2m_cfg.get("warn_pct_distance", 0.03))
    if proposal.m2m_flip_distance_pct < reject_pct:
        signals.append(FailureSignal(
            code="M2M_TOO_CLOSE",
            severity="REJECT",
            message=(f"M2M flip is {proposal.m2m_flip_distance_pct:.2%} from "
                     f"spot (< {reject_pct:.2%})"),
        ))
    elif proposal.m2m_flip_distance_pct < warn_pct:
        signals.append(FailureSignal(
            code="M2M_NEAR",
            severity="WARN",
            message=(f"M2M flip is {proposal.m2m_flip_distance_pct:.2%} from "
                     f"spot (< {warn_pct:.2%})"),
        ))

    # Short-strike approach distance.
    sa_cfg = cfg.get("short_strike_approach", {})
    short_dist = abs(proposal.short_strike - proposal.underlying_price) / max(
        proposal.underlying_price, 1e-6)
    if short_dist < float(sa_cfg.get("reject_pct", 0.01)):
        signals.append(FailureSignal(
            code="SHORT_STRIKE_TOO_CLOSE",
            severity="REJECT",
            message=f"short strike {short_dist:.2%} from spot",
        ))
    elif short_dist < float(sa_cfg.get("warn_pct", 0.02)):
        signals.append(FailureSignal(
            code="SHORT_STRIKE_NEAR",
            severity="WARN",
            message=f"short strike only {short_dist:.2%} from spot",
        ))

    # Gamma window — don't open right before expiration.
    gamma_cfg = cfg.get("gamma", {})
    dte = (proposal.expiration - date.today()).days
    no_open = int(gamma_cfg.get("no_open_dte", 5))
    if dte <= no_open:
        signals.append(FailureSignal(
            code="GAMMA_NO_OPEN",
            severity="REJECT",
            message=f"{dte} DTE inside no-open window ({no_open})",
        ))

    return signals


# --- post-entry monitoring --------------------------------------------------


def evaluate_open_position(state: PositionState,
                           cfg: Optional[Dict[str, Any]] = None) -> List[FailureSignal]:
    """Generate exit / warn signals for a live position."""
    cfg = cfg or load_config("failure_logic")
    signals: List[FailureSignal] = []
    p = state.proposal

    # Loss tolerance.
    tol = cfg.get("loss_tolerance", {})
    max_loss_mult = float(tol.get("max_loss_mult_of_credit", 2.0))
    max_loss_pct_width = float(tol.get("max_loss_pct_of_width", 0.60))
    max_loss_dollars = tol.get("max_loss_dollars_per_spread")  # may be None
    unrealized = state.unrealized_pl_per_spread
    if unrealized < 0:
        loss = -unrealized
        if p.credit > 0 and loss >= max_loss_mult * p.credit:
            signals.append(FailureSignal(
                code="MAX_LOSS_MULT",
                severity="EXIT",
                message=f"loss {loss:.2f} >= {max_loss_mult}x credit ({p.credit:.2f})",
            ))
        if p.width > 0 and loss >= max_loss_pct_width * p.width:
            signals.append(FailureSignal(
                code="MAX_LOSS_PCT_WIDTH",
                severity="EXIT",
                message=f"loss {loss:.2f} >= {max_loss_pct_width:.0%} of width",
            ))
        if max_loss_dollars is not None and loss >= float(max_loss_dollars):
            # The client's "-$200 rule" — hard dollar stop independent of
            # credit/width geometry. Stored as the per-spread option-price
            # unit (so 2.00 == $200/contract since options are quoted in
            # 100-unit lots).
            signals.append(FailureSignal(
                code="MAX_LOSS_DOLLARS",
                severity="EXIT",
                message=(f"loss {loss:.2f} >= hard dollar stop "
                         f"{float(max_loss_dollars):.2f} per spread"),
            ))

    # M2M proximity flag (live).
    m2m = cfg.get("m2m", {})
    dist_pct = abs(p.m2m_flip_price - state.current_underlying) / max(
        state.current_underlying, 1e-6)
    if dist_pct < float(m2m.get("warn_pct_distance", 0.03)):
        signals.append(FailureSignal(
            code="M2M_PROXIMITY_LIVE",
            severity="WARN",
            message=f"underlying {dist_pct:.2%} from M2M flip {p.m2m_flip_price:.2f}",
        ))

    # Gamma window — escalate as expiration nears.
    gcfg = cfg.get("gamma", {})
    dte = state.days_to_expiration
    if dte <= int(gcfg.get("force_close_dte", 2)):
        signals.append(FailureSignal(
            code="GAMMA_FORCE_CLOSE",
            severity="EXIT",
            message=f"DTE {dte} inside force-close window",
        ))
    elif dte <= int(gcfg.get("hot_dte", 7)):
        signals.append(FailureSignal(
            code="GAMMA_HOT",
            severity="WARN",
            message=f"DTE {dte} — gamma rising, scale toward exit",
        ))

    # Profit target hit.
    if state.current_spread_mark <= p.exit_50pct_target_credit:
        signals.append(FailureSignal(
            code="PROFIT_TARGET_50",
            severity="EXIT",
            message=f"mark {state.current_spread_mark:.2f} hit 50% target",
        ))
    elif state.current_spread_mark <= p.exit_25pct_target_credit:
        signals.append(FailureSignal(
            code="PROFIT_TARGET_25",
            severity="INFO",
            message=f"mark {state.current_spread_mark:.2f} hit 25% target",
        ))

    return signals
