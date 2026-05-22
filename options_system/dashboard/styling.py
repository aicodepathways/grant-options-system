"""Shared visual styling — colors, page config, and one CSS injection."""
from __future__ import annotations

import streamlit as st


# Streamlit 1.50 deprecated `use_container_width=True` in favor of
# `width="stretch"`. We support both runtimes via this shim — pages call
# WIDTH_STRETCH wherever they used to write `use_container_width=True`.
def _detect_width_kwarg() -> dict:
    try:
        major, minor = (int(x) for x in st.__version__.split(".")[:2])
    except ValueError:
        return {"use_container_width": True}
    if (major, minor) >= (1, 46):
        return {"width": "stretch"}
    return {"use_container_width": True}


WIDTH_STRETCH = _detect_width_kwarg()


# Color palette — calm, professional, dark-text on light backgrounds.
PALETTE = {
    "deploy_green":  "#2e7d4f",
    "deploy_amber":  "#b07d2c",
    "deploy_red":    "#a4373a",
    "neutral_gray":  "#5a5a5a",
    "accent_blue":   "#1f4e79",
    "soft_bg":       "#f6f7f9",
    "rank_top":      "#dceedf",
    "rank_mid":      "#fff1cf",
    "rank_low":      "#fadcdc",
}


def configure_page(title: str, icon: str = "📊", layout: str = "wide") -> None:
    """Per-page config plus shared CSS injection. Call at top of every page."""
    st.set_page_config(
        page_title=f"{title} — Options Income System",
        page_icon=icon,
        layout=layout,
        initial_sidebar_state="expanded",
    )
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)


def regime_color(regime: str | None, deploy: bool | None = None) -> str:
    if deploy is False:
        return PALETTE["deploy_red"]
    if regime in {"PANIC", "LOW_VOL_NO_EDGE"}:
        return PALETTE["deploy_red"]
    if regime in {"ELEVATED_VOL", "BREAKOUT"}:
        return PALETTE["deploy_amber"]
    if regime in {"BENIGN_TREND", "BENIGN_CHOP", "COMPRESSION"}:
        return PALETTE["deploy_green"]
    return PALETTE["neutral_gray"]


def rank_color(rank: int, total: int) -> str:
    """Background color for a candidate row based on its rank position."""
    if total <= 0:
        return PALETTE["soft_bg"]
    pct = rank / max(total - 1, 1)
    if pct <= 0.33:
        return PALETTE["rank_top"]
    if pct <= 0.67:
        return PALETTE["rank_mid"]
    return PALETTE["rank_low"]


_GLOBAL_CSS = """
<style>
/* Tighten Streamlit's defaults so the dashboard doesn't feel airy. */
.block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1280px; }
h1, h2, h3 { font-weight: 600; letter-spacing: -0.01em; }

/* Status pill used for regime + deploy. */
.status-pill {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 999px;
    font-weight: 600;
    color: white;
    font-size: 0.95rem;
    letter-spacing: 0.02em;
}

/* Metric-card grid. */
.metric-card {
    background: #f6f7f9;
    border: 1px solid #e3e5e8;
    border-radius: 10px;
    padding: 1rem 1.25rem;
}
.metric-card .label {
    color: #6b6f76; font-size: 0.8rem; text-transform: uppercase;
    letter-spacing: 0.05em; margin-bottom: 0.25rem;
}
.metric-card .value {
    color: #1f2329; font-size: 1.4rem; font-weight: 600;
}
.metric-card .delta {
    color: #5a5a5a; font-size: 0.85rem; margin-top: 0.2rem;
}

/* Trade card frame. */
.trade-card {
    border: 1px solid #d8dde2;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    background: #ffffff;
    margin-bottom: 1rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.trade-card h4 { margin-top: 0; color: #1f2329; }

/* Reason / flag list */
.reasons { color: #5a5a5a; font-size: 0.9rem; margin-left: 0.25rem; }
.reasons li { margin: 0.15rem 0; }

/* Hide Streamlit's default badges in production-feel mode. */
header [data-testid="stStatusWidget"] { display: none; }
</style>
"""
