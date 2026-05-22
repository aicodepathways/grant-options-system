"""Universe scanner.

Iterates each ticker in the configured universe and emits a Candidate when:
- price/volume floor is met
- IV is within configured band
- realized-vol compression confirms (optional)
- there is at least one usable expiration in DTE window with quality chain

The scanner returns lightweight metadata; chains stay cached on the adapter
for the trade builder to reuse without a second fetch.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Optional

import pandas as pd

from ..config import load_config
from ..data import MarketDataAdapter, OptionChain, get_adapter

logger = logging.getLogger(__name__)


@dataclass
class Candidate:
    symbol: str
    is_index_product: bool
    underlying_price: float
    avg_iv: float
    iv_rank: Optional[float]
    atr: float
    atr_compression_ratio: Optional[float]
    bb_width_compression_ratio: Optional[float]
    expirations_in_window: List[date] = field(default_factory=list)
    quality_score: float = 0.0
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "is_index_product": self.is_index_product,
            "underlying_price": self.underlying_price,
            "avg_iv": self.avg_iv,
            "iv_rank": self.iv_rank,
            "atr": self.atr,
            "atr_compression_ratio": self.atr_compression_ratio,
            "bb_width_compression_ratio": self.bb_width_compression_ratio,
            "expirations_in_window": [d.isoformat() for d in self.expirations_in_window],
            "quality_score": self.quality_score,
            "reasons": list(self.reasons),
        }


class Scanner:
    def __init__(self, adapter: Optional[MarketDataAdapter] = None) -> None:
        self.adapter = adapter or get_adapter()
        self.scanner_cfg = load_config("scanner_config")
        self.strategy_cfg = load_config("strategy_rules")

    # --- public ------------------------------------------------------------

    def universe(self) -> List[str]:
        u = self.scanner_cfg.get("universe", {}) or {}
        return list(u.get("index_etfs", [])) + list(u.get("equities", []))

    def index_products(self) -> set[str]:
        return set(self.strategy_cfg.get("buffers", {}).get("index_products", []))

    def scan(self) -> List[Candidate]:
        out: List[Candidate] = []
        max_n = int(self.scanner_cfg.get("output", {}).get("max_candidates_per_run", 25))
        for symbol in self.universe():
            try:
                cand = self._evaluate(symbol)
            except Exception as exc:
                logger.warning("Scanner failed on %s: %s", symbol, exc)
                continue
            if cand is not None:
                out.append(cand)

        out.sort(key=lambda c: c.quality_score, reverse=True)
        return out[:max_n]

    # --- per-symbol evaluation ---------------------------------------------

    def _evaluate(self, symbol: str) -> Optional[Candidate]:
        reasons: List[str] = []

        # 1. Price/volume floor.
        hist = self.adapter.get_history(symbol, period="6mo")
        if hist is None or len(hist) < 30:
            return None
        last_close = float(hist["close"].iloc[-1])
        avg_dollar_vol = float((hist["close"] * hist["volume"]).tail(20).mean())
        liq_cfg = self.scanner_cfg.get("liquidity", {})
        if avg_dollar_vol < float(liq_cfg.get("min_underlying_dollar_volume", 5_000_000)):
            return None

        # 2. DTE window expirations.
        dte_cfg = self.strategy_cfg.get("dte", {})
        dmin, dmax = int(dte_cfg.get("min", 14)), int(dte_cfg.get("max", 21))
        today = date.today()
        try:
            all_exps = self.adapter.get_expirations(symbol)
        except Exception as exc:
            logger.warning("No expirations for %s: %s", symbol, exc)
            return None
        in_window = [e for e in all_exps if dmin <= (e - today).days <= dmax]
        if not in_window:
            return None

        # 3. Pull a representative chain (the nearest valid expiration) for IV/quality.
        try:
            chain = self.adapter.get_option_chain(symbol, in_window[0])
        except Exception as exc:
            logger.warning("Chain fetch failed for %s @ %s: %s", symbol, in_window[0], exc)
            return None

        avg_iv = self._chain_avg_iv(chain)
        if avg_iv is None:
            logger.debug("%s: no near-ATM IV available", symbol)
            return None

        iv_cfg = self.scanner_cfg.get("iv", {})
        iv_min, iv_max = float(iv_cfg.get("min", 0.15)), float(iv_cfg.get("max", 0.80))
        if not (iv_min <= avg_iv <= iv_max):
            logger.debug("%s rejected: avg IV %.2f outside [%.2f, %.2f]",
                         symbol, avg_iv, iv_min, iv_max)
            return None

        # 4. IV-rank approximation (yfinance has no historical IV; we proxy
        # using realized vol percentile over the long lookback).
        iv_rank = self._iv_rank_proxy(hist)
        iv_rank_min = iv_cfg.get("iv_rank_min")
        if iv_rank is not None and iv_rank_min is not None and iv_rank < float(iv_rank_min):
            reasons.append(f"IV-rank proxy {iv_rank:.2f} < min {iv_rank_min}")
            return None

        # 5. Liquidity at the chain level.
        if not self._chain_liquidity_ok(chain):
            logger.debug("%s rejected: chain liquidity below thresholds", symbol)
            return None

        # 6. Compression filters (optional).
        atr = self._atr(hist)
        atr_ratio = self._atr_compression_ratio(hist)
        bb_ratio = self._bb_width_compression_ratio(hist)

        comp_cfg = self.scanner_cfg.get("compression", {})
        if comp_cfg.get("enabled", True):
            atr_cap = float(comp_cfg.get("atr_compression_pct", 0.75))
            bb_cap = float(comp_cfg.get("bb_width_compression_pct", 0.65))
            atr_ok = atr_ratio is not None and atr_ratio <= atr_cap
            bb_ok = bb_ratio is not None and bb_ratio <= bb_cap
            if not (atr_ok or bb_ok):
                logger.debug(
                    "%s rejected: no compression (atr_ratio=%s, bb_ratio=%s)",
                    symbol, atr_ratio, bb_ratio,
                )
                return None

        # 7. Score.
        score = self._score(
            avg_iv=avg_iv,
            iv_rank=iv_rank,
            atr_ratio=atr_ratio,
            bb_ratio=bb_ratio,
            avg_dollar_vol=avg_dollar_vol,
        )

        return Candidate(
            symbol=symbol,
            is_index_product=symbol in self.index_products(),
            underlying_price=last_close,
            avg_iv=avg_iv,
            iv_rank=iv_rank,
            atr=atr,
            atr_compression_ratio=atr_ratio,
            bb_width_compression_ratio=bb_ratio,
            expirations_in_window=in_window,
            quality_score=score,
            reasons=reasons or ["passed all filters"],
        )

    # --- helpers ------------------------------------------------------------

    @staticmethod
    def _chain_avg_iv(chain: OptionChain) -> Optional[float]:
        """Near-ATM IV average. We deliberately exclude deep wings: the BS
        solver overshoots there, and the smile biases a whole-chain average
        far above realistic at-the-money vol — which the trade builder then
        uses to compute expected move."""
        spot = chain.underlying_price
        if spot <= 0:
            return None
        # Take contracts whose strike is within 5% of spot, both rights.
        band = spot * 0.05
        near = [
            c for c in chain.all_contracts()
            if abs(c.strike - spot) <= band and c.iv is not None and c.iv > 0
        ]
        if not near:
            return None
        # Median is more robust than mean against a stray solver spike.
        ivs = sorted(c.iv for c in near)
        mid = len(ivs) // 2
        return (ivs[mid] if len(ivs) % 2 else (ivs[mid - 1] + ivs[mid]) / 2.0)

    def _chain_liquidity_ok(self, chain: OptionChain) -> bool:
        liq_cfg = self.scanner_cfg.get("liquidity", {})
        max_spread = float(liq_cfg.get("max_bid_ask_spread_pct", 0.10))
        min_oi = int(liq_cfg.get("min_open_interest", 100))
        # At-the-money region: contracts within 10% of underlying.
        atm_band = chain.underlying_price * 0.10
        near_atm = [
            c for c in chain.all_contracts()
            if abs(c.strike - chain.underlying_price) <= atm_band
        ]
        if not near_atm:
            return False
        good = [
            c for c in near_atm
            if c.spread_pct <= max_spread and c.open_interest >= min_oi
        ]
        return len(good) >= max(3, len(near_atm) // 4)

    @staticmethod
    def _atr(hist: pd.DataFrame, period: int = 14) -> float:
        h, l, c = hist["high"], hist["low"], hist["close"]
        tr = pd.concat(
            [(h - l), (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1
        ).max(axis=1)
        return float(tr.rolling(period).mean().iloc[-1])

    @staticmethod
    def _atr_compression_ratio(
        hist: pd.DataFrame, period: int = 14, lookback: int = 50
    ) -> Optional[float]:
        if len(hist) < period + lookback:
            return None
        h, l, c = hist["high"], hist["low"], hist["close"]
        tr = pd.concat(
            [(h - l), (h - c.shift()).abs(), (l - c.shift()).abs()], axis=1
        ).max(axis=1)
        atr = tr.rolling(period).mean()
        return float(atr.iloc[-1] / atr.tail(lookback).mean())

    @staticmethod
    def _bb_width_compression_ratio(
        hist: pd.DataFrame, period: int = 20
    ) -> Optional[float]:
        if len(hist) < period * 2:
            return None
        c = hist["close"]
        sma = c.rolling(period).mean()
        std = c.rolling(period).std()
        width = ((sma + 2 * std) - (sma - 2 * std)) / sma
        return float(width.iloc[-1] / width.rolling(period * 2).mean().iloc[-1])

    @staticmethod
    def _iv_rank_proxy(hist: pd.DataFrame, lookback: int = 252) -> Optional[float]:
        """Realized-vol percentile over the past year. Crude proxy for IV-rank."""
        if len(hist) < 30:
            return None
        rets = hist["close"].pct_change().dropna()
        rolling_vol = rets.rolling(20).std() * (252 ** 0.5)
        recent = rolling_vol.iloc[-1]
        window = rolling_vol.tail(lookback).dropna()
        if window.empty or pd.isna(recent):
            return None
        return float((window < recent).mean())

    def _score(
        self,
        avg_iv: float,
        iv_rank: Optional[float],
        atr_ratio: Optional[float],
        bb_ratio: Optional[float],
        avg_dollar_vol: float,
    ) -> float:
        # Higher = better. IV in the middle of the band is preferred; deeper
        # compression is preferred; more dollar volume is preferred.
        iv_cfg = self.scanner_cfg.get("iv", {})
        iv_min = float(iv_cfg.get("min", 0.15))
        iv_max = float(iv_cfg.get("max", 0.80))
        iv_center = (iv_min + iv_max) / 2.0
        iv_score = 1.0 - abs(avg_iv - iv_center) / max(iv_max - iv_center, 1e-6)

        comp = []
        if atr_ratio is not None:
            comp.append(1.0 - min(atr_ratio, 1.5))
        if bb_ratio is not None:
            comp.append(1.0 - min(bb_ratio, 1.5))
        comp_score = sum(comp) / len(comp) if comp else 0.0

        liq_score = min(avg_dollar_vol / 50_000_000, 1.0)
        rank_score = float(iv_rank) if iv_rank is not None else 0.5

        return (
            0.35 * iv_score
            + 0.30 * comp_score
            + 0.20 * liq_score
            + 0.15 * rank_score
        )
