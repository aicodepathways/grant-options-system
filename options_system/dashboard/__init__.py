"""Streamlit dashboard.

Wraps the existing pipeline (regime / scanner / builder / validator /
execution / logging) in a clean multi-page UI for client-facing review.
No business logic here — pages call the same modules `main.py` does.

Run with:
    streamlit run options_system/dashboard/app.py
"""
