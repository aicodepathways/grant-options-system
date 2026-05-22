"""Black-Scholes greek estimation and implied-vol solver.

yfinance returns implied vol on most contracts but greeks are inconsistent.
We compute them from price + IV when needed. When IV is missing we back it
out from mid price via a Brent solver.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

try:
    from scipy.stats import norm
    from scipy.optimize import brentq
    _HAS_SCIPY = True
except ImportError:  # pragma: no cover
    _HAS_SCIPY = False


@dataclass
class Greeks:
    delta: float
    gamma: float
    theta: float
    vega: float
    price: float


def _norm_cdf(x: float) -> float:
    if _HAS_SCIPY:
        return float(norm.cdf(x))
    # Abramowitz-Stegun fallback.
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def black_scholes_greeks(
    spot: float,
    strike: float,
    t_years: float,
    rate: float,
    iv: float,
    right: str,
) -> Greeks:
    """Standard Black-Scholes-Merton greeks (no dividends).

    Returns greeks per 1.0 underlying move and theta per calendar day.
    """
    if t_years <= 0 or iv <= 0 or spot <= 0 or strike <= 0:
        intrinsic = max(0.0, (spot - strike) if right.upper().startswith("C")
                        else (strike - spot))
        return Greeks(delta=0.0, gamma=0.0, theta=0.0, vega=0.0, price=intrinsic)

    sqrt_t = math.sqrt(t_years)
    d1 = (math.log(spot / strike) + (rate + 0.5 * iv * iv) * t_years) / (iv * sqrt_t)
    d2 = d1 - iv * sqrt_t

    pdf_d1 = _norm_pdf(d1)
    is_call = right.upper().startswith("C")

    if is_call:
        price = spot * _norm_cdf(d1) - strike * math.exp(-rate * t_years) * _norm_cdf(d2)
        delta = _norm_cdf(d1)
        theta_yr = (-spot * pdf_d1 * iv / (2 * sqrt_t)
                    - rate * strike * math.exp(-rate * t_years) * _norm_cdf(d2))
    else:
        price = strike * math.exp(-rate * t_years) * _norm_cdf(-d2) - spot * _norm_cdf(-d1)
        delta = _norm_cdf(d1) - 1.0
        theta_yr = (-spot * pdf_d1 * iv / (2 * sqrt_t)
                    + rate * strike * math.exp(-rate * t_years) * _norm_cdf(-d2))

    gamma = pdf_d1 / (spot * iv * sqrt_t)
    vega = spot * pdf_d1 * sqrt_t / 100.0   # per 1 vol point (1%)
    theta = theta_yr / 365.0                # per calendar day

    return Greeks(delta=delta, gamma=gamma, theta=theta, vega=vega, price=price)


def implied_vol(
    market_price: float,
    spot: float,
    strike: float,
    t_years: float,
    rate: float,
    right: str,
    lo: float = 1e-4,
    hi: float = 5.0,
) -> Optional[float]:
    """Back IV out of an option's mid price via Brent's method.

    Returns None when scipy isn't installed or the price is outside the
    no-arbitrage envelope.
    """
    if not _HAS_SCIPY or t_years <= 0 or spot <= 0 or strike <= 0:
        return None
    intrinsic = max(0.0, (spot - strike) if right.upper().startswith("C")
                    else (strike - spot))
    if market_price < intrinsic:
        return None

    def diff(vol: float) -> float:
        return black_scholes_greeks(spot, strike, t_years, rate, vol, right).price - market_price

    try:
        return float(brentq(diff, lo, hi, maxiter=100, xtol=1e-5))
    except (ValueError, RuntimeError):
        return None
