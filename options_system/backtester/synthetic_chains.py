"""Synthetic options-chain generator for backtesting.

THIS IS AN APPROXIMATION. We do not have access to historical bid/ask quotes
in yfinance, so we generate chains using Black-Scholes priced from:
- The historical close as the underlying.
- Realized vol over a trailing window as a proxy for IV.
- A simple term-structure adjustment so longer-dated options carry slightly
  higher IV.
- A flat IV smile (skew is ignored in Phase 1).

For every meaningful result, **flag this approximation in the output**. To
swap in real historical chains later, implement SyntheticChainSource and
register it via BacktestAdapter.
"""
from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Iterable, List, Optional

import numpy as np
import pandas as pd

from ..config import load_config
from ..data import (
    MarketDataAdapter,
    OptionChain,
    OptionContract,
    Quote,
    black_scholes_greeks,
    get_adapter,
)


class SyntheticChainSource(ABC):
    """Hook so a real historical-chain provider can replace the synthesizer."""
    approximate: bool = True

    @abstractmethod
    def chain_on(
        self, symbol: str, as_of: date, expiration: date, underlying_price: float
    ) -> OptionChain: ...


@dataclass
class _BSChainConfig:
    iv_anchor: float = 0.20         # fallback when realized vol can't be computed
    iv_term_slope: float = 0.05     # extra IV per year of additional term
    rate: float = 0.045
    n_strikes: int = 21             # OTM + ATM + OTM
    strike_step_pct: float = 0.01   # spacing between strikes
    spread_pct: float = 0.04        # bid-ask spread as fraction of mid
    open_interest: int = 1000
    volume: int = 100


class BlackScholesChainSource(SyntheticChainSource):
    """Default synthesizer: flat-smile BSM with a small term-structure tilt."""
    approximate = True

    def __init__(self, history: pd.DataFrame,
                 cfg: Optional[_BSChainConfig] = None) -> None:
        self.history = history.copy()
        self.history.index = pd.to_datetime(self.history.index).tz_localize(None)
        self.cfg = cfg or _BSChainConfig()

    def chain_on(
        self, symbol: str, as_of: date, expiration: date, underlying_price: float
    ) -> OptionChain:
        cfg = self.cfg
        t_years = max((expiration - as_of).days, 0) / 365.0
        if t_years <= 0:
            return OptionChain(symbol=symbol, expiration=expiration,
                               underlying_price=underlying_price)

        rv = self._realized_vol(as_of)
        atm_iv = max(rv if rv is not None else cfg.iv_anchor, 0.05)
        iv_at_t = atm_iv + cfg.iv_term_slope * (t_years - 30 / 365.0)
        iv_at_t = max(iv_at_t, 0.05)

        spot = underlying_price
        step = max(spot * cfg.strike_step_pct, 0.50)
        # Center strikes on round dollar (or half) increments.
        atm = round(spot / step) * step
        half = (cfg.n_strikes - 1) // 2
        strikes = [atm + (i - half) * step for i in range(cfg.n_strikes)]
        strikes = [round(s, 2) for s in strikes if s > 0]

        calls: List[OptionContract] = []
        puts: List[OptionContract] = []
        for k in strikes:
            for right, bucket in (("C", calls), ("P", puts)):
                g = black_scholes_greeks(spot, k, t_years, cfg.rate, iv_at_t, right)
                mid = max(g.price, 0.01)
                half_spread = max(mid * cfg.spread_pct / 2.0, 0.01)
                bucket.append(OptionContract(
                    symbol=symbol,
                    expiration=expiration,
                    strike=float(k),
                    right=right,
                    bid=round(mid - half_spread, 2),
                    ask=round(mid + half_spread, 2),
                    last=round(mid, 2),
                    volume=cfg.volume,
                    open_interest=cfg.open_interest,
                    iv=iv_at_t,
                    delta=g.delta,
                    gamma=g.gamma,
                    theta=g.theta,
                    vega=g.vega,
                    contract_symbol=f"{symbol}{expiration:%y%m%d}{right}{int(k*1000):08d}",
                ))
        return OptionChain(symbol=symbol, expiration=expiration,
                           underlying_price=spot, calls=calls, puts=puts)

    def _realized_vol(self, as_of: date, window: int = 20) -> Optional[float]:
        idx = self.history.index <= pd.Timestamp(as_of)
        sliced = self.history[idx]
        if len(sliced) < window + 1:
            return None
        rets = sliced["close"].pct_change().dropna().iloc[-window:]
        if rets.empty:
            return None
        return float(rets.std() * math.sqrt(252))


class BacktestAdapter(MarketDataAdapter):
    """Adapter that serves historical data + synthetic chains as if live.

    Wraps the live adapter for OHLCV history, then synthesizes chains for any
    (symbol, expiration) pair. The current "as-of" date is mutable and
    advanced by the Backtester each iteration.
    """
    name = "backtest"

    def __init__(
        self,
        live_adapter: Optional[MarketDataAdapter] = None,
        chain_source_cls: type = BlackScholesChainSource,
    ) -> None:
        self.live = live_adapter or get_adapter()
        self.cfg = load_config("data_config")
        self._as_of: date = date.today()
        self._chain_sources: dict[str, SyntheticChainSource] = {}
        self._chain_source_cls = chain_source_cls
        self._histories: dict[str, pd.DataFrame] = {}

    @property
    def as_of(self) -> date:
        return self._as_of

    def set_as_of(self, when: date) -> None:
        self._as_of = when

    def _full_history(self, symbol: str) -> pd.DataFrame:
        if symbol not in self._histories:
            self._histories[symbol] = self.live.get_history(
                symbol, period=self.cfg.get("history", {}).get("long_period", "2y")
            )
        return self._histories[symbol]

    def _sliced(self, symbol: str) -> pd.DataFrame:
        df = self._full_history(symbol)
        return df[df.index <= pd.Timestamp(self._as_of)]

    def _chain_source(self, symbol: str) -> SyntheticChainSource:
        if symbol not in self._chain_sources:
            self._chain_sources[symbol] = self._chain_source_cls(
                history=self._full_history(symbol)
            )
        return self._chain_sources[symbol]

    # --- adapter API ------------------------------------------------------

    def get_quote(self, symbol: str) -> Quote:
        sliced = self._sliced(symbol)
        if sliced.empty:
            raise RuntimeError(f"no history for {symbol} as of {self._as_of}")
        last = float(sliced["close"].iloc[-1])
        vol = int(sliced["volume"].iloc[-1])
        return Quote(symbol=symbol, last=last, bid=None, ask=None,
                     volume=vol, timestamp=datetime.combine(self._as_of, datetime.min.time()))

    def get_history(self, symbol: str, period: str = "6mo",
                    interval: str = "1d") -> pd.DataFrame:
        # Ignore `period` in favor of the slice-up-to-as-of view.
        return self._sliced(symbol).copy()

    def get_expirations(self, symbol: str) -> List[date]:
        # Synthesize weekly expirations 7-45 days out so the scanner's DTE
        # window always finds candidates.
        return [self._as_of + timedelta(days=d) for d in (7, 14, 21, 28, 35, 45)]

    def get_option_chain(self, symbol: str, expiration: date) -> OptionChain:
        underlying = self.get_quote(symbol).last
        return self._chain_source(symbol).chain_on(
            symbol=symbol, as_of=self._as_of, expiration=expiration,
            underlying_price=underlying,
        )

    def get_vix(self) -> Quote:
        return self.get_quote("^VIX")

    def get_vix_history(self, period: str = "6mo") -> pd.DataFrame:
        return self._sliced("^VIX").copy()
