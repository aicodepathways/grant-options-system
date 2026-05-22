"""Streamlit dashboard entrypoint.

Run with:
    streamlit run options_system/dashboard/app.py

The four pages live under `pages/` and Streamlit auto-discovers them via
its native multi-page layout. This file is the landing page.
"""
from __future__ import annotations

import logging
from pathlib import Path

import streamlit as st

from options_system.dashboard.components import regime_banner, replay_banner, sidebar_controls
from options_system.dashboard.styling import configure_page

# Quiet yfinance/peewee at import time too.
for noisy in ("yfinance", "peewee", "urllib3", "requests", "curl_cffi"):
    logging.getLogger(noisy).setLevel(logging.WARNING)


def main() -> None:
    configure_page("Overview", icon="📈")
    st.title("Options Income System")
    st.caption("Premium-selling pipeline · regime → scan → build → validate")

    run = sidebar_controls()
    replay_banner(run)
    regime_banner(run.regime)

    st.markdown("---")

    # Quick-stat row.
    cols = st.columns(4)
    with cols[0]:
        st.metric("Stages completed", " → ".join(run.stages_completed) or "—")
    with cols[1]:
        st.metric("Candidates", len(run.candidates))
    with cols[2]:
        st.metric("Proposals built", len(run.proposals))
    with cols[3]:
        valid = sum(1 for v in run.validations if v.valid)
        st.metric("Validated VALID", f"{valid} / {len(run.validations)}")

    st.markdown("### Today's Pipeline")
    if run.regime is None:
        st.warning("Pipeline has not produced a regime reading yet.")
        return

    if not run.regime.deploy:
        st.error(
            f"NO-TRADE day — regime **{run.regime.regime.replace('_', ' ')}**. "
            f"Pipeline gates closed at the regime stage."
        )
        with st.expander("Why?"):
            for r in run.regime.reasons:
                st.write(f"- {r}")
        return

    st.success(
        f"DEPLOY day — regime **{run.regime.regime.replace('_', ' ')}** "
        f"(size mult {run.regime.size_mult:.2f}). Use the sidebar to navigate "
        f"to **Today's Candidates** for ranked trade ideas, or **Trade Detail** "
        f"to inspect any single proposal."
    )

    if not run.candidates:
        st.info("Regime is open but no candidates passed the scanner today.")
        return
    st.write(
        f"**{len(run.candidates)}** candidates passed scanner filters; "
        f"**{len(run.proposals)}** trade proposals were built. "
        f"See the **Today's Candidates** page for the ranked table."
    )

    with st.expander("Configuration in use"):
        from options_system.config import load_all
        cfg = load_all()
        st.code(
            "\n".join(f"{k}.yaml" for k in cfg.keys())
            + "\nLoaded from: " + str(Path(__file__).resolve().parents[1] / "config"),
            language="text",
        )


if __name__ == "__main__":
    main()
