"""yfinance implementation of MarketDataAdapter.

yfinance specifics handled here:
- options chains via Ticker.options + Ticker.option_chain()
- IV usually present per contract; greeks are not — we estimate via Black-Scholes
- VIX symbol is "^VIX"
- aggressive caching to dodge Yahoo's rate limits
- retry-with-backoff because the API is flaky
"""
from __future__ import annotations

import logging
import math
import time
from datetime import date, datetime
from typing import Any, List, Optional

import pandas as pd

from ..config import load_config
from .base import MarketDataAdapter, OptionChain, OptionContract, Quote
from .cache import cached
from .greeks import black_scholes_greeks, implied_vol


def _safe_float(value: Any, default: float = 0.0) -> float:
    """yfinance frequently returns NaN/None in volume, OI, bid, ask cells.
    `x or default` is unsafe — `NaN or 0` returns NaN. Use this instead.
    """
    if value is None:
        return default
    try:
        f = float(value)
    except (TypeError, ValueError):
        return default
    if math.isnan(f) or math.isinf(f):
        return default
    return f


def _safe_int(value: Any, default: int = 0) -> int:
    return int(_safe_float(value, float(default)))

logger = logging.getLogger(__name__)

try:
    import yfinance as yf
    _HAS_YF = True
except ImportError:  # pragma: no cover
    _HAS_YF = False


class YFinanceAdapter(MarketDataAdapter):
    name = "yfinance"
    VIX_SYMBOL = "^VIX"
    SPX_SYMBOL = "^GSPC"

    def __init__(self) -> None:
        if not _HAS_YF:
            raise ImportError(
                "yfinance is required. Install with `pip install yfinance`."
            )
        cfg = load_config("data_config")
        self.rate = float(cfg.get("risk_free_rate", 0.045))
        retry_cfg = cfg.get("retries", {}) or {}
        self.max_attempts = int(retry_cfg.get("max_attempts", 3))
        self.backoff = float(retry_cfg.get("backoff_base_seconds", 1.5))
        hist_cfg = cfg.get("history", {}) or {}
        self.default_period = str(hist_cfg.get("default_period", "6mo"))
        self._tickers: dict[str, "yf.Ticker"] = {}

    # --- internal helpers ----------------------------------------------------

    def _ticker(self, symbol: str) -> "yf.Ticker":
        if symbol not in self._tickers:
            self._tickers[symbol] = yf.Ticker(symbol)
        return self._tickers[symbol]

    def _retry(self, fn, *args, **kwargs):
        last_exc: Optional[Exception] = None
        for attempt in range(self.max_attempts):
            try:
                return fn(*args, **kwargs)
            except Exception as exc:  # yfinance raises a wide variety
                last_exc = exc
                wait = self.backoff * (2 ** attempt)
                logger.warning(
                    "yfinance call %s failed (attempt %d/%d): %s; sleeping %.1fs",
                    fn.__name__, attempt + 1, self.max_attempts, exc, wait,
                )
                time.sleep(wait)
        # Wrap with a friendlier message so the dashboard / pipeline can show
        # something useful instead of leaking yfinance internals.
        kind = type(last_exc).__name__ if last_exc else "Exception"
        msg = str(last_exc) or repr(last_exc)
        raise RuntimeError(
            f"Yahoo Finance data fetch failed ({kind}: {msg}). "
            f"This is usually a transient Yahoo API issue; retry in a minute."
        )

    # --- abstract method implementations -------------------------------------

    @cached(namespace="quote", ttl_key="quote")
    def get_quote(self, symbol: str) -> Quote:
        ticker = self._ticker(symbol)

        def _fetch() -> Quote:
            # `fast_info` is the cheapest path; falls back to history.
            try:
                fi = ticker.fast_info
                last = float(fi.get("last_price") or fi.get("lastPrice") or 0.0)
                bid = fi.get("bid")
                ask = fi.get("ask")
                volume = fi.get("last_volume") or fi.get("volume")
            except Exception:
                last, bid, ask, volume = 0.0, None, None, None

            if last <= 0:
                hist = ticker.history(period="5d", interval="1d")
                if hist.empty:
                    raise RuntimeError(f"No quote data for {symbol}")
                last = float(hist["Close"].iloc[-1])
                volume = int(hist["Volume"].iloc[-1])

            return Quote(
                symbol=symbol,
                last=last,
                bid=float(bid) if bid else None,
                ask=float(ask) if ask else None,
                volume=int(volume) if volume else None,
                timestamp=datetime.utcnow(),
            )

        return self._retry(_fetch)

    @cached(namespace="history", ttl_key="history")
    def get_history(
        self, symbol: str, period: str = "6mo", interval: str = "1d"
    ) -> pd.DataFrame:
        ticker = self._ticker(symbol)

        def _fetch() -> pd.DataFrame:
            df = ticker.history(period=period, interval=interval, auto_adjust=False)
            if df.empty:
                raise RuntimeError(f"No history for {symbol}")
            df = df.rename(
                columns={"Open": "open", "High": "high", "Low": "low",
                         "Close": "close", "Volume": "volume"}
            )
            df.index = pd.to_datetime(df.index).tz_localize(None)
            return df[["open", "high", "low", "close", "volume"]]

        return self._retry(_fetch)

    @cached(namespace="expirations", ttl_key="chain")
    def get_expirations(self, symbol: str) -> List[date]:
        ticker = self._ticker(symbol)

        def _fetch() -> List[date]:
            raw = ticker.options or ()
            return [datetime.strptime(s, "%Y-%m-%d").date() for s in raw]

        return self._retry(_fetch)

    @cached(namespace="chain", ttl_key="chain")
    def get_option_chain(self, symbol: str, expiration: date) -> OptionChain:
        ticker = self._ticker(symbol)
        underlying = self.get_quote(symbol).last
        exp_str = expiration.strftime("%Y-%m-%d")

        def _fetch() -> OptionChain:
            chain = ticker.option_chain(exp_str)
            calls = self._df_to_contracts(
                chain.calls, symbol, expiration, "C", underlying)
            puts = self._df_to_contracts(
                chain.puts, symbol, expiration, "P", underlying)
            return OptionChain(
                symbol=symbol,
                expiration=expiration,
                underlying_price=underlying,
                calls=calls,
                puts=puts,
            )

        return self._retry(_fetch)

    @cached(namespace="vix", ttl_key="vix")
    def get_vix(self) -> Quote:
        return self.get_quote(self.VIX_SYMBOL)

    @cached(namespace="vix_history", ttl_key="history")
    def get_vix_history(self, period: str = "6mo") -> pd.DataFrame:
        return self.get_history(self.VIX_SYMBOL, period=period)

    # --- chain conversion ----------------------------------------------------

    def _df_to_contracts(
        self,
        df: pd.DataFrame,
        symbol: str,
        expiration: date,
        right: str,
        underlying_price: float,
    ) -> List[OptionContract]:
        if df is None or df.empty:
            return []
        today = date.today()
        t_years = max((expiration - today).days, 0) / 365.0
        out: List[OptionContract] = []

        for _, row in df.iterrows():
            strike = _safe_float(row.get("strike"))
            if strike <= 0:
                continue

            bid = _safe_float(row.get("bid"))
            ask = _safe_float(row.get("ask"))
            last = _safe_float(row.get("lastPrice"))
            mid = (bid + ask) / 2.0 if (ask > 0 and bid >= 0) else last

            iv_raw = _safe_float(row.get("impliedVolatility"))
            iv: Optional[float] = iv_raw if iv_raw > 0 else None
            if iv is None and mid > 0 and t_years > 0:
                iv = implied_vol(
                    market_price=mid,
                    spot=underlying_price,
                    strike=strike,
                    t_years=t_years,
                    rate=self.rate,
                    right=right,
                )

            delta = gamma = theta = vega = None
            if iv is not None and t_years > 0:
                g = black_scholes_greeks(
                    spot=underlying_price,
                    strike=strike,
                    t_years=t_years,
                    rate=self.rate,
                    iv=iv,
                    right=right,
                )
                delta, gamma, theta, vega = g.delta, g.gamma, g.theta, g.vega

            contract_symbol = row.get("contractSymbol")
            if isinstance(contract_symbol, float) and math.isnan(contract_symbol):
                contract_symbol = None

            out.append(OptionContract(
                symbol=symbol,
                expiration=expiration,
                strike=strike,
                right=right,
                bid=bid,
                ask=ask,
                last=last,
                volume=_safe_int(row.get("volume")),
                open_interest=_safe_int(row.get("openInterest")),
                iv=iv,
                delta=delta,
                gamma=gamma,
                theta=theta,
                vega=vega,
                contract_symbol=contract_symbol,
            ))
        return out
