"""Hard-reject behavior: severe builder flags must fail validation outright.

Uses a bare Validator with stubbed regime engine so no network is touched —
the hard-reject block runs before any chain refetch.
"""
from __future__ import annotations

from datetime import date, timedelta

from options_system.trade_builder import TradeLeg, TradeProposal
from options_system.validator import Validator
from options_system.validator.validator import ValidationResult


class _StubRegime:
    def __init__(self, deploy=True):
        self._deploy = deploy

    def evaluate(self):
        class R:
            regime = "BENIGN_TREND"
            deploy = True
            size_mult = 1.0
            reasons = []
            metrics = {}

            def to_dict(self):
                return {"regime": self.regime, "deploy": self.deploy}
        return R()


def _bare_validator(hard_rejects_cfg) -> Validator:
    v = object.__new__(Validator)
    v.adapter = None                      # never reached in these tests
    v.regime_engine = _StubRegime()
    v.scanner_cfg = {}
    v.failure_cfg = {"hard_rejects": hard_rejects_cfg}
    return v


def _proposal(resilience=0.5, flags=None):
    exp = date.today() + timedelta(days=16)
    return TradeProposal(
        symbol="QQQ", strategy="BEAR_CALL", expiration=exp,
        underlying_price=713.78,
        legs=[
            TradeLeg("SELL", "C", 729.0, exp, mid=1.65),
            TradeLeg("BUY", "C", 734.0, exp, mid=0.90),
        ],
        credit=1.65, width=5.0, max_loss=3.35, pop=0.67,
        m2m_flip_price=721.69, m2m_flip_distance_pct=0.011,
        expiration_breakeven_price=730.65,
        expiration_breakeven_distance_pct=0.024,
        expected_move=29.0, atr=11.0,
        early_red_pl_score=resilience,
        exit_50pct_target_credit=0.82, exit_25pct_target_credit=1.24,
        est_days_to_50pct=7, est_days_to_25pct=3,
        flags=list(flags or []),
        mode="opportunity",
    )


def test_zero_resilience_is_invalid():
    v = _bare_validator({"enabled": True, "max_rejectable_resilience": 0.10})
    result = v.validate(_proposal(resilience=0.0))
    assert result.valid is False
    assert any("resilience" in r for r in result.reasons)


def test_m2m_too_close_flag_is_invalid():
    v = _bare_validator({"enabled": True, "honor_m2m_too_close_flag": True})
    result = v.validate(_proposal(resilience=0.5, flags=["M2M_TOO_CLOSE"]))
    assert result.valid is False
    assert any("M2M_TOO_CLOSE" in r for r in result.reasons)


def test_disabled_hard_rejects_do_not_gate():
    """With hard_rejects disabled, the check falls through to live checks
    (which fail differently here because adapter is None — but crucially
    NOT with a hard-reject reason)."""
    v = _bare_validator({"enabled": False})
    result = v.validate(_proposal(resilience=0.0, flags=["M2M_TOO_CLOSE"]))
    assert not any("hard-reject" in r for r in result.reasons)
