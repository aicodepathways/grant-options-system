"""Regime Overview — current regime status, VIX & SPX charts, deploy
decision with reasoning."""
from __future__ import annotations

# --- Streamlit Cloud path fix (see options_system/dashboard/app.py for context) ---
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import pandas as pd
import streamlit as st

from options_system.dashboard.components import (
    line_chart, metric_card, regime_banner, replay_banner, sidebar_controls,
)
from options_system.dashboard.state import get_components
from options_system.dashboard.styling import WIDTH_STRETCH, PALETTE, configure_page


def main() -> None:
    configure_page("Regime Overview", icon="🌡️")
    st.title("Regime Overview")
    st.caption("VIX bands · SPX trend & compression · DEPLOY/NO-TRADE gate")

    run = sidebar_controls()
    replay_banner(run)
    regime_banner(run.regime)
    st.markdown("---")

    if run.regime is None:
        st.warning("Regime has not been evaluated yet.")
        return

    # --- top-row metrics ---
    metrics = run.regime.metrics
    cols = st.columns(4)
    with cols[0]:
        metric_card("VIX", f"{metrics.get('vix', 0):.2f}",
                    delta=f"1d move: {metrics.get('vix_spike_1d_pct', 0):+.2%}"
                    if metrics.get("vix_spike_1d_pct") is not None else "")
    with cols[1]:
        bbw = metrics.get("bb_width")
        bbw_avg = metrics.get("bb_width_avg")
        ratio_str = f"{(bbw / bbw_avg):.0%} of avg" if bbw and bbw_avg else "—"
        metric_card("SPX BB-width",
                    f"{bbw:.4f}" if bbw is not None else "—",
                    delta=ratio_str)
    with cols[2]:
        metric_card("Trend state", str(metrics.get("trend_state", "—")).title())
    with cols[3]:
        metric_card("Breakout state",
                    str(metrics.get("breakout_state", "—")).replace("_", " ").title())

    # --- reasoning ---
    st.markdown("### Why this regime?")
    if not run.regime.reasons:
        st.info("Engine returned no reasons — fall-through path.")
    else:
        for r in run.regime.reasons:
            st.markdown(f"- {r}")

    # --- charts ---
    st.markdown("### Market Context")
    components = get_components()
    adapter = components["adapter"]

    chart_cols = st.columns(2)
    with chart_cols[0]:
        try:
            vix_hist = adapter.get_vix_history(period="6mo")
            line_chart(vix_hist, "close", "VIX (6mo)", height=320,
                       overlays=_vix_band_overlays(vix_hist))
        except Exception as exc:
            st.error(f"Failed to load VIX history: {exc}")

    with chart_cols[1]:
        try:
            spx_hist = adapter.get_history(
                getattr(adapter, "SPX_SYMBOL", "^GSPC"), period="6mo")
            line_chart(spx_hist, "close", "SPX (^GSPC, 6mo)", height=320,
                       overlays=_spx_sma_overlays(spx_hist))
        except Exception as exc:
            st.error(f"Failed to load SPX history: {exc}")

    # --- deployment / config table ---
    st.markdown("### Regime → Deployment Map")
    from options_system.config import load_config
    deploy_map = load_config("regime_config").get("deployment", {})
    rows = []
    for regime_name, rule in deploy_map.items():
        rows.append({
            "Regime": regime_name.replace("_", " ").title(),
            "Deploy": "✅" if rule.get("deploy") else "🛑",
            "Size mult": f"{float(rule.get('size_mult', 0)):.2f}",
            "Active": "← current" if regime_name == run.regime.regime else "",
        })
    st.dataframe(pd.DataFrame(rows), **WIDTH_STRETCH, hide_index=True)


def _vix_band_overlays(vix_hist: pd.DataFrame) -> dict:
    from options_system.config import load_config
    vix_cfg = load_config("regime_config").get("vix", {})
    out: dict = {}
    for label, key in [("Too low", "too_low"), ("Benign max", "benign_max"),
                       ("Elevated max", "elevated_max"), ("Panic", "panic")]:
        v = vix_cfg.get(key)
        if v is None:
            continue
        out[f"{label} ({v})"] = pd.Series(
            [v] * len(vix_hist), index=vix_hist.index)
    return out


def _spx_sma_overlays(spx_hist: pd.DataFrame) -> dict:
    from options_system.config import load_config
    spx_cfg = load_config("regime_config").get("spx", {})
    fast = int(spx_cfg.get("sma_fast", 20))
    slow = int(spx_cfg.get("sma_slow", 50))
    if len(spx_hist) < slow:
        return {}
    return {
        f"SMA{fast}": spx_hist["close"].rolling(fast).mean(),
        f"SMA{slow}": spx_hist["close"].rolling(slow).mean(),
    }


main()
