"""Black-Scholes sanity checks."""
from __future__ import annotations

import math

from options_system.data.greeks import black_scholes_greeks


def test_call_delta_in_range():
    g = black_scholes_greeks(spot=100.0, strike=100.0, t_years=30/365,
                             rate=0.045, iv=0.25, right="C")
    assert 0.0 <= g.delta <= 1.0
    assert g.gamma > 0
    assert g.theta < 0
    assert g.vega > 0


def test_put_delta_in_range():
    g = black_scholes_greeks(spot=100.0, strike=100.0, t_years=30/365,
                             rate=0.045, iv=0.25, right="P")
    assert -1.0 <= g.delta <= 0.0


def test_put_call_parity_approximately_holds():
    s, k, t, r, iv = 100.0, 100.0, 30/365, 0.045, 0.25
    c = black_scholes_greeks(s, k, t, r, iv, "C").price
    p = black_scholes_greeks(s, k, t, r, iv, "P").price
    parity = c - p - (s - k * math.exp(-r * t))
    assert abs(parity) < 1e-3


def test_zero_time_returns_intrinsic():
    g = black_scholes_greeks(spot=110.0, strike=100.0, t_years=0.0,
                             rate=0.045, iv=0.25, right="C")
    assert g.price == 10.0
    assert g.delta == 0.0
