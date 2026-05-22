"""Data layer.

The `MarketDataAdapter` ABC defines the contract every data provider must
satisfy. Business logic depends only on the ABC, never on yfinance directly,
so the source can be swapped to Tradier / Polygon / a broker API later.
"""
from .base import MarketDataAdapter, OptionContract, OptionChain, Quote
from .factory import get_adapter
from .greeks import black_scholes_greeks, implied_vol

__all__ = [
    "MarketDataAdapter",
    "OptionContract",
    "OptionChain",
    "Quote",
    "get_adapter",
    "black_scholes_greeks",
    "implied_vol",
]
