"""Pure-function tests for the regime classifier — no network calls."""
from __future__ import annotations

import pandas as pd
import pytest

from options_system.config import load_config
from options_system.regime_engine import classify


def _flat_history(value: float, n: int = 100) -> pd.DataFrame:
    idx = pd.date_range(end="2024-01-01", periods=n, freq="B")
    return pd.DataFrame({
        "open": [value] * n, "high": [value * 1.005] * n,
        "low": [value * 0.995] * n, "close": [value] * n,
        "volume": [1_000_000] * n,
    }, index=idx)


@pytest.fixture(scope="module")
def cfg():
    return load_config("regime_config")


def test_panic_when_vix_above_threshold(cfg):
    spx = _flat_history(4500.0)
    vix = _flat_history(35.0)
    r = classify(vix_level=35.0, vix_history=vix, spx_history=spx, cfg=cfg)
    assert r.regime == "PANIC"
    assert r.deploy is False


def test_low_vol_when_vix_too_low(cfg):
    spx = _flat_history(4500.0)
    vix = _flat_history(10.0)
    r = classify(vix_level=10.0, vix_history=vix, spx_history=spx, cfg=cfg)
    assert r.regime == "LOW_VOL_NO_EDGE"
    assert r.deploy is False


def test_benign_path_emits_deployable_state(cfg):
    spx = _flat_history(4500.0)
    vix = _flat_history(15.0)
    r = classify(vix_level=15.0, vix_history=vix, spx_history=spx, cfg=cfg)
    assert r.deploy is True
    assert r.regime in {"BENIGN_TREND", "BENIGN_CHOP", "COMPRESSION"}
