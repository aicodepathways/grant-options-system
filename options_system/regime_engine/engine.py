"""Rules-based regime classifier.

Decision tree:
1. VIX panic level or 1d spike    -> PANIC          (NO-TRADE)
2. VIX too low                    -> LOW_VOL_NO_EDGE (NO-TRADE)
3. SPX breakout/breakdown         -> BREAKOUT
4. Bollinger-width compression    -> COMPRESSION
5. VIX elevated                   -> ELEVATED_VOL
6. Trend filter (SPX > slow SMA)  -> BENIGN_TREND else BENIGN_CHOP

Each step short-circuits. Reasoning strings are attached to the reading so
downstream logging can show the user *why* deployment was gated on/off.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from ..config import load_config
from ..data import MarketDataAdapter, get_adapter


@dataclass
class RegimeReading:
    regime: str
    deploy: bool
    size_mult: float
    reasons: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "regime": self.regime,
            "deploy": self.deploy,
            "size_mult": self.size_mult,
            "reasons": list(self.reasons),
            "metrics": dict(self.metrics),
            "timestamp": self.timestamp.isoformat(),
        }


class RegimeEngine:
    def __init__(self, adapter: Optional[MarketDataAdapter] = None) -> None:
        self.adapter = adapter or get_adapter()
        self.cfg = load_config("regime_config")

    # --- public API ----------------------------------------------------------

    def evaluate(self) -> RegimeReading:
        vix_quote = self.adapter.get_vix()
        vix_hist = self.adapter.get_vix_history(period="3mo")
        spx_hist = self.adapter.get_history(
            self.adapter_spx_symbol(), period="6mo")

        return classify(
            vix_level=vix_quote.last,
            vix_history=vix_hist,
            spx_history=spx_hist,
            cfg=self.cfg,
        )

    def adapter_spx_symbol(self) -> str:
        # SPX cash index isn't directly tradable on yfinance; ^GSPC is the
        # proxy. Adapters may override.
        return getattr(self.adapter, "SPX_SYMBOL", "^GSPC")


# --- pure-function classifier (testable without a live data source) ---------


def classify(
    vix_level: float,
    vix_history: pd.DataFrame,
    spx_history: pd.DataFrame,
    cfg: Dict[str, Any],
) -> RegimeReading:
    """Pure-function form of the classifier — easy to unit-test."""
    vix_cfg = cfg.get("vix", {})
    spx_cfg = cfg.get("spx", {})
    deploy_cfg = cfg.get("deployment", {})

    metrics: Dict[str, Any] = {"vix": vix_level}
    reasons: List[str] = []

    # 1. VIX spike check.
    spike_pct = _vix_spike_pct(vix_history)
    metrics["vix_spike_1d_pct"] = spike_pct
    if spike_pct is not None and spike_pct >= float(vix_cfg.get("spike_pct_1d", 0.20)):
        reasons.append(f"VIX 1d spike {spike_pct:.1%} >= threshold")
        return _emit("PANIC", deploy_cfg, reasons, metrics)

    # 2. Absolute VIX bands.
    if vix_level >= float(vix_cfg.get("panic", 32.0)):
        reasons.append(f"VIX {vix_level:.2f} >= panic threshold")
        return _emit("PANIC", deploy_cfg, reasons, metrics)
    if vix_level <= float(vix_cfg.get("too_low", 12.0)):
        reasons.append(f"VIX {vix_level:.2f} <= floor — premium too cheap")
        return _emit("LOW_VOL_NO_EDGE", deploy_cfg, reasons, metrics)

    # 3. SPX breakout / breakdown.
    breakout_state = _detect_breakout(spx_history, spx_cfg)
    metrics["breakout_state"] = breakout_state
    if breakout_state in ("breakout_up", "breakout_down"):
        reasons.append(f"SPX {breakout_state.replace('_', ' ')}")
        return _emit("BREAKOUT", deploy_cfg, reasons, metrics)

    # 4. Bollinger-width compression.
    bb_width, bb_avg = _bb_width_metrics(spx_history, spx_cfg)
    metrics["bb_width"] = bb_width
    metrics["bb_width_avg"] = bb_avg
    compression_pct = float(spx_cfg.get("bb_width_compression_pct", 0.5))
    if bb_width is not None and bb_avg and bb_width <= bb_avg * compression_pct:
        reasons.append(
            f"SPX BB-width compressed: {bb_width:.4f} <= "
            f"{compression_pct:.0%} of avg {bb_avg:.4f}"
        )
        return _emit("COMPRESSION", deploy_cfg, reasons, metrics)

    # 5. Elevated VIX (but not panic).
    if vix_level > float(vix_cfg.get("benign_max", 20.0)):
        reasons.append(f"VIX {vix_level:.2f} elevated (>{vix_cfg.get('benign_max')})")
        return _emit("ELEVATED_VOL", deploy_cfg, reasons, metrics)

    # 6. Trend vs chop.
    trend_state = _trend_state(spx_history, spx_cfg)
    metrics["trend_state"] = trend_state
    if trend_state == "trend":
        reasons.append("SPX above slow SMA — benign trend")
        return _emit("BENIGN_TREND", deploy_cfg, reasons, metrics)

    reasons.append("SPX below slow SMA, no compression — benign chop")
    return _emit("BENIGN_CHOP", deploy_cfg, reasons, metrics)


# --- internals ---------------------------------------------------------------


def _emit(
    regime: str,
    deploy_cfg: Dict[str, Any],
    reasons: List[str],
    metrics: Dict[str, Any],
) -> RegimeReading:
    rule = deploy_cfg.get(regime, {"deploy": False, "size_mult": 0.0})
    return RegimeReading(
        regime=regime,
        deploy=bool(rule.get("deploy", False)),
        size_mult=float(rule.get("size_mult", 0.0)),
        reasons=reasons,
        metrics=metrics,
    )


def _vix_spike_pct(vix_history: pd.DataFrame) -> Optional[float]:
    if vix_history is None or len(vix_history) < 2:
        return None
    closes = vix_history["close"].dropna()
    if len(closes) < 2:
        return None
    prev, curr = float(closes.iloc[-2]), float(closes.iloc[-1])
    if prev <= 0:
        return None
    return (curr - prev) / prev


def _detect_breakout(spx_history: pd.DataFrame, spx_cfg: Dict[str, Any]) -> str:
    lookback = int(spx_cfg.get("breakout_lookback", 20))
    buf = float(spx_cfg.get("breakout_buffer", 0.005))
    if spx_history is None or len(spx_history) < lookback + 1:
        return "none"
    window = spx_history.iloc[-(lookback + 1):-1]
    last = float(spx_history["close"].iloc[-1])
    hi, lo = float(window["high"].max()), float(window["low"].min())
    if last >= hi * (1 + buf):
        return "breakout_up"
    if last <= lo * (1 - buf):
        return "breakout_down"
    return "none"


def _bb_width_metrics(spx_history: pd.DataFrame, spx_cfg: Dict[str, Any]):
    period = int(spx_cfg.get("bb_period", 20))
    n_std = float(spx_cfg.get("bb_std", 2.0))
    if spx_history is None or len(spx_history) < period * 2:
        return None, None
    closes = spx_history["close"]
    sma = closes.rolling(period).mean()
    std = closes.rolling(period).std()
    upper = sma + n_std * std
    lower = sma - n_std * std
    width = (upper - lower) / sma
    if width.dropna().empty:
        return None, None
    current = float(width.iloc[-1])
    avg = float(width.rolling(period * 2).mean().iloc[-1])
    return current, avg


def _trend_state(spx_history: pd.DataFrame, spx_cfg: Dict[str, Any]) -> str:
    slow = int(spx_cfg.get("sma_slow", 50))
    if spx_history is None or len(spx_history) < slow:
        return "unknown"
    closes = spx_history["close"]
    sma_slow = closes.rolling(slow).mean().iloc[-1]
    last = float(closes.iloc[-1])
    return "trend" if last > sma_slow else "chop"
