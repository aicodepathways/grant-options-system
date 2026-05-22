"""Backtesting framework.

Runs the scanner -> builder -> validator pipeline on historical data. Equity
and VIX history come from the live data adapter (yfinance via cache).
Historical option chains are synthesized from a Black-Scholes term-structure
model — explicitly an APPROXIMATION, not real reconstructed historical
chains. Swap in Polygon / CBOE Datashop later via the SyntheticChainSource
interface.
"""
from .synthetic_chains import SyntheticChainSource, BacktestAdapter
from .engine import Backtester, BacktestResult, TradeOutcome

__all__ = [
    "SyntheticChainSource",
    "BacktestAdapter",
    "Backtester",
    "BacktestResult",
    "TradeOutcome",
]
