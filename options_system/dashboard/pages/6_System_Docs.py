"""System Docs — renders the repo README inside the public dashboard.

The GitHub repo is private, so the README link 404s for anyone without
repo access. The dashboard, however, is public. This page reads the
README straight off disk at runtime (so it is always in sync with the
deployed code) and offers it two ways:

- a rendered view for humans
- a raw copy block for pasting into an AI advisor (Chat / ChatGPT / Claude)

No pipeline run is triggered here; the page is instant.
"""
from __future__ import annotations

# --- Streamlit Cloud path fix (see options_system/dashboard/app.py for context) ---
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import streamlit as st

from options_system.dashboard.styling import configure_page

README_PATH = Path(__file__).resolve().parents[3] / "README.md"


def main() -> None:
    configure_page("System Docs", icon="📖")
    st.title("System Docs")
    st.caption(
        "The full system README, always in sync with the deployed code. "
        "Use the Copy tab to paste the whole thing into your AI advisor."
    )

    if not README_PATH.exists():
        st.error(
            "README.md not found in the deployment. This is a packaging "
            "issue, not a data issue. Contact Brendan."
        )
        return

    text = README_PATH.read_text()

    rendered_tab, copy_tab = st.tabs(["📄 Read", "📋 Copy for AI advisor"])

    with rendered_tab:
        st.markdown(text)

    with copy_tab:
        st.caption(
            "Click the copy icon in the top-right corner of the block below, "
            "then paste into Chat at the start of a session so it has full "
            "system context."
        )
        st.code(text, language="markdown")


main()
