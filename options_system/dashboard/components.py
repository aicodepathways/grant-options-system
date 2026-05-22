"""Shared UI components used by multiple pages."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from ..regime_engine import RegimeReading
from .state import PipelineRun, get_or_create_run
from .styling import WIDTH_STRETCH, PALETTE, regime_color


def sidebar_controls() -> PipelineRun:
    """Controls common to every page: refresh, top-N, force-deploy, dry-run.

    Includes a Replay toggle that runs the pipeline against the
    BacktestAdapter set to a chosen historical date — useful for showing
    populated pages when today's live regime is too benign to surface trades.
    """
    from datetime import date, timedelta

    st.sidebar.title("Pipeline Controls")

    mode = st.sidebar.radio(
        "Mode",
        ["Live", "Replay (past date)"],
        horizontal=True,
        help="Replay uses the backtester's synthetic chains for any past date — "
             "real OHLCV/VIX history, IV from realized vol (no skew).",
    )
    replay_date = None
    if mode.startswith("Replay"):
        today = date.today()
        default = today - timedelta(days=4)
        replay_date = st.sidebar.date_input(
            "Replay as-of date",
            value=default,
            min_value=today - timedelta(days=365 * 2),
            max_value=today - timedelta(days=1),
        )
        st.sidebar.caption(
            "⚠️ Synthetic chains — IVs from realized vol, no skew. Use for "
            "demo / illustrative purposes, not absolute P/L analysis."
        )

    top_n = st.sidebar.slider("Validate top N", 1, 10, 5)
    force_deploy = st.sidebar.checkbox(
        "Force deploy (override regime gate)", value=False,
        help="Run scanner/builder even if regime says NO-TRADE. Research mode only.",
    )
    skip_validation = st.sidebar.checkbox(
        "Skip real-time validator", value=False,
        help="Build proposals without re-fetching chains for validation.",
    )
    refresh = st.sidebar.button("🔄  Refresh data", **WIDTH_STRETCH)
    run = get_or_create_run(
        force_refresh=refresh,
        replay_date=replay_date,
        top_n=top_n,
        force_deploy=force_deploy,
        skip_validation=skip_validation,
    )
    if run.replay_date is not None:
        st.sidebar.caption(f"Replay: **{run.replay_date.isoformat()}**")
    else:
        st.sidebar.caption(f"Last live run (UTC): {run.run_at:%Y-%m-%d %H:%M}")
    if run.error:
        st.sidebar.error(f"Pipeline error:\n{run.error}")
    return run


def replay_banner(run: PipelineRun) -> None:
    """Visible note on every page when the user is viewing a historical replay.

    Keeps the user from confusing replay candidates with live ones.
    """
    if run.replay_date is None:
        return
    st.info(
        f"📼 **Replay mode** — showing pipeline output for "
        f"**{run.replay_date.isoformat()}**. Chains are synthetic "
        "(BSM with realized-vol IV proxy, no skew); regime/SPX/VIX values "
        "are real historical data.",
        icon="📼",
    )


def status_pill(text: str, color: str) -> None:
    st.markdown(
        f"<span class='status-pill' style='background:{color};'>{text}</span>",
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, delta: Optional[str] = None) -> None:
    delta_html = f"<div class='delta'>{delta}</div>" if delta else ""
    st.markdown(
        f"<div class='metric-card'>"
        f"<div class='label'>{label}</div>"
        f"<div class='value'>{value}</div>{delta_html}</div>",
        unsafe_allow_html=True,
    )


def regime_banner(regime: Optional[RegimeReading]) -> None:
    """Top-of-page regime pill + deploy state."""
    if regime is None:
        st.warning("Regime not yet evaluated.")
        return
    color = regime_color(regime.regime, regime.deploy)
    deploy_text = "DEPLOY" if regime.deploy else "NO-TRADE"
    cols = st.columns([1, 1, 4])
    with cols[0]:
        status_pill(regime.regime.replace("_", " "), color)
    with cols[1]:
        deploy_color = PALETTE["deploy_green"] if regime.deploy else PALETTE["deploy_red"]
        status_pill(deploy_text, deploy_color)
    with cols[2]:
        st.caption(
            f"Size mult: **{regime.size_mult:.2f}** · "
            f"Evaluated: {regime.timestamp:%Y-%m-%d %H:%M UTC}"
        )


def line_chart(
    df: pd.DataFrame,
    y_col: str = "close",
    title: str = "",
    height: int = 280,
    overlays: Optional[dict] = None,
) -> None:
    """Plotly line chart, restyled to match the dashboard.

    `overlays` is a dict of {name: pd.Series} — drawn as dashed grey lines.
    """
    if df is None or df.empty:
        st.info(f"No data for {title}.")
        return
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=df[y_col],
        mode="lines", name=title or y_col,
        line=dict(color=PALETTE["accent_blue"], width=2),
    ))
    for name, series in (overlays or {}).items():
        fig.add_trace(go.Scatter(
            x=series.index, y=series.values, mode="lines", name=name,
            line=dict(color=PALETTE["neutral_gray"], width=1, dash="dot"),
        ))
    fig.update_layout(
        title=title, height=height,
        margin=dict(l=10, r=10, t=40, b=20),
        plot_bgcolor="white",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#eef0f2"),
        legend=dict(orientation="h", y=-0.15),
    )
    # plotly_chart in Streamlit 1.50 forwards extra kwargs to Plotly config and
    # warns. use_container_width is still accepted explicitly here.
    st.plotly_chart(fig, use_container_width=True)
