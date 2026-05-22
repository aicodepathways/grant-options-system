"""Failure-logic rule tests — no I/O."""
from __future__ import annotations

from datetime import date, timedelta

from options_system.failure_logic import (
    PositionState,
    evaluate_open_position,
    evaluate_proposal,
)
from options_system.trade_builder import TradeLeg, TradeProposal


def _proposal(m2m_dist_pct=0.10, dte=18, spot=100.0):
    exp = date.today() + timedelta(days=dte)
    return TradeProposal(
        symbol="TEST",
        strategy="BULL_PUT",
        expiration=exp,
        underlying_price=spot,
        legs=[
            TradeLeg("SELL", "P", 95.0, exp, mid=1.20, bid=1.15, ask=1.25),
            TradeLeg("BUY", "P", 92.5, exp, mid=0.50, bid=0.45, ask=0.55),
        ],
        credit=0.70, width=2.5, max_loss=1.80, pop=0.80,
        m2m_flip_price=spot * (1 - m2m_dist_pct),
        m2m_flip_distance_pct=m2m_dist_pct,
        expiration_breakeven_price=spot * (1 - max(m2m_dist_pct, 0.03)),
        expiration_breakeven_distance_pct=max(m2m_dist_pct, 0.03),
        expected_move=2.0, atr=1.5,
        early_red_pl_score=0.7,
        exit_50pct_target_credit=0.35,
        exit_25pct_target_credit=0.525,
        est_days_to_50pct=7,
        est_days_to_25pct=3,
    )


def test_proposal_rejects_when_m2m_too_close():
    sigs = evaluate_proposal(_proposal(m2m_dist_pct=0.005))
    assert any(s.code == "M2M_TOO_CLOSE" and s.severity == "REJECT" for s in sigs)


def test_proposal_warns_when_m2m_near():
    sigs = evaluate_proposal(_proposal(m2m_dist_pct=0.025))
    assert any(s.code == "M2M_NEAR" and s.severity == "WARN" for s in sigs)


def test_proposal_rejects_inside_no_open_window():
    sigs = evaluate_proposal(_proposal(dte=3))
    assert any(s.code == "GAMMA_NO_OPEN" for s in sigs)


def test_open_position_emits_profit_target():
    p = _proposal()
    state = PositionState(
        proposal=p,
        current_underlying=p.underlying_price,
        current_spread_mark=p.exit_50pct_target_credit - 0.01,
        days_held=4,
    )
    sigs = evaluate_open_position(state)
    assert any(s.code == "PROFIT_TARGET_50" and s.severity == "EXIT" for s in sigs)


def test_open_position_triggers_hard_dollar_stop():
    """Client's -$200 rule: loss >= max_loss_dollars_per_spread exits."""
    p = _proposal()
    # Spread bought back at credit + $2.50 → loss of $2.50/spread ($250 / contract)
    state = PositionState(
        proposal=p,
        current_underlying=p.underlying_price * 0.98,
        current_spread_mark=p.credit + 2.50,
        days_held=3,
    )
    cfg = {"loss_tolerance": {
        "max_loss_mult_of_credit": 99.0,         # disable other triggers
        "max_loss_pct_of_width": 99.0,
        "max_loss_dollars_per_spread": 2.00,     # $200/contract stop
    }}
    sigs = evaluate_open_position(state, cfg=cfg)
    assert any(s.code == "MAX_LOSS_DOLLARS" and s.severity == "EXIT" for s in sigs)


def test_open_position_force_close_at_2_dte():
    p = _proposal(dte=2)
    state = PositionState(
        proposal=p,
        current_underlying=p.underlying_price,
        current_spread_mark=0.40,
        days_held=16,
    )
    sigs = evaluate_open_position(state)
    assert any(s.code == "GAMMA_FORCE_CLOSE" for s in sigs)
