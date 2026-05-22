"""Abstract market-data adapter contract.

Anything in `scanner/`, `regime_engine/`, `trade_builder/`, etc. talks to this
ABC, never to a concrete provider. To swap yfinance for Tradier or Polygon,
implement these methods and register the new adapter in `factory.py`.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional

import pandas as pd


@dataclass
class Quote:
    symbol: str
    last: float
    bid: Optional[float]
    ask: Optional[float]
    volume: Optional[int]
    timestamp: datetime

    @property
    def mid(self) -> float:
        if self.bid is not None and self.ask is not None and self.ask > 0:
            return (self.bid + self.ask) / 2.0
        return self.last


@dataclass
class OptionContract:
    symbol: str           # underlying
    expiration: date
    strike: float
    right: str            # 'C' or 'P'
    bid: float
    ask: float
    last: float
    volume: int
    open_interest: int
    iv: Optional[float] = None        # implied vol (annualized, decimal)
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None
    contract_symbol: Optional[str] = None  # provider-specific OCC symbol

    @property
    def mid(self) -> float:
        if self.ask > 0 and self.bid >= 0:
            return (self.bid + self.ask) / 2.0
        return self.last

    @property
    def spread_pct(self) -> float:
        m = self.mid
        if m <= 0:
            return float("inf")
        return (self.ask - self.bid) / m


@dataclass
class OptionChain:
    symbol: str
    expiration: date
    underlying_price: float
    calls: List[OptionContract] = field(default_factory=list)
    puts: List[OptionContract] = field(default_factory=list)

    def all_contracts(self) -> List[OptionContract]:
        return self.calls + self.puts


class MarketDataAdapter(ABC):
    """Provider-agnostic market data interface.

    Implementations must be thread-safe at the method level (the daily
    workflow does not currently parallelize, but the backtester might).
    """

    name: str = "abstract"

    @abstractmethod
    def get_quote(self, symbol: str) -> Quote:
        """Latest quote for an equity / index / ETF."""

    @abstractmethod
    def get_history(
        self,
        symbol: str,
        period: str = "6mo",
        interval: str = "1d",
    ) -> pd.DataFrame:
        """OHLCV history. DataFrame indexed by date with columns:
        open, high, low, close, volume.
        """

    @abstractmethod
    def get_expirations(self, symbol: str) -> List[date]:
        """List available option expiration dates for the symbol."""

    @abstractmethod
    def get_option_chain(self, symbol: str, expiration: date) -> OptionChain:
        """Full chain (calls + puts) for one expiration."""

    @abstractmethod
    def get_vix(self) -> Quote:
        """Current VIX quote."""

    @abstractmethod
    def get_vix_history(self, period: str = "6mo") -> pd.DataFrame:
        """VIX OHLCV history."""

    # --- Convenience helpers built on top of the abstract methods. ---

    def get_chains_for_dte_window(
        self, symbol: str, dte_min: int, dte_max: int
    ) -> List[OptionChain]:
        """All chains whose DTE falls within the window."""
        today = date.today()
        out: List[OptionChain] = []
        for exp in self.get_expirations(symbol):
            dte = (exp - today).days
            if dte_min <= dte <= dte_max:
                out.append(self.get_option_chain(symbol, exp))
        return out
