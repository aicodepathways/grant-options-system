"""Log Viewer — searchable history of past scans, regimes, and trades.

Reads JSONL files written by `logging_system.DailyLogger`. One folder per
calendar date, four streams (candidates, decisions, trades, events).
"""
from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

from options_system.config import logs_dir
from options_system.dashboard.components import replay_banner, sidebar_controls
from options_system.dashboard.styling import WIDTH_STRETCH, configure_page

STREAMS = ("candidates", "decisions", "trades", "events")


def main() -> None:
    configure_page("Log Viewer", icon="🗂️")
    st.title("Log Viewer")
    st.caption("Searchable history of pipeline runs — JSONL streams")

    # We don't run the pipeline here, but the sidebar still drives common state.
    run = sidebar_controls()
    replay_banner(run)
    st.markdown("---")

    log_root = logs_dir()
    available_dates = sorted(
        [p.name for p in log_root.iterdir() if p.is_dir()],
        reverse=True,
    )
    if not available_dates:
        st.info("No logs on disk yet. Run the daily pipeline (CLI or this "
                "dashboard) at least once to generate logs.")
        return

    # --- filters ---
    cols = st.columns([2, 2, 4])
    with cols[0]:
        chosen_date = st.selectbox("Date", available_dates, index=0)
    with cols[1]:
        chosen_streams = st.multiselect(
            "Streams", STREAMS, default=list(STREAMS),
        )
    with cols[2]:
        search = st.text_input(
            "Search (substring match in payload)", value="",
            placeholder="e.g. 'SPY', 'BULL_PUT', 'PANIC'",
        )

    folder = log_root / chosen_date
    records = _load_records(folder, chosen_streams)
    if search:
        s = search.lower()
        records = [r for r in records if s in json.dumps(r).lower()]

    st.caption(f"{len(records)} record(s) at {folder}")

    if not records:
        st.warning("No records match the active filters.")
        return

    # Group by stream so the user can drill in.
    tabs = st.tabs([s.title() for s in STREAMS if s in chosen_streams])
    for tab, stream in zip(tabs, [s for s in STREAMS if s in chosen_streams]):
        with tab:
            _render_stream(stream, [r for r in records if r["stream"] == stream])


def _load_records(folder: Path, streams) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for stream in streams:
        path = folder / f"{stream}.jsonl"
        if not path.exists():
            continue
        with path.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                out.append(rec)
    out.sort(key=lambda r: r.get("ts", ""))
    return out


def _render_stream(stream: str, records: List[Dict[str, Any]]) -> None:
    if not records:
        st.info(f"No records in `{stream}.jsonl` for this filter.")
        return

    if stream == "candidates":
        rows = []
        for r in records:
            d = r.get("data", {})
            rows.append({
                "ts": _fmt_ts(r["ts"]),
                "symbol": d.get("symbol"),
                "score": _round(d.get("quality_score"), 3),
                "avg_iv": _pct(d.get("avg_iv")),
                "iv_rank": d.get("iv_rank"),
                "atr": _round(d.get("atr"), 2),
                "expirations": ", ".join(d.get("expirations_in_window", [])),
            })
        st.dataframe(rows, **WIDTH_STRETCH, hide_index=True)
        return

    if stream == "decisions":
        # Decisions are typed with a `kind` field.
        for r in records:
            data = r.get("data", {})
            kind = data.get("kind", "—")
            payload = data.get("payload", {})
            with st.expander(
                f"[{_fmt_ts(r['ts'])}]  {kind}  —  "
                f"{_decision_summary(kind, payload)}"
            ):
                st.json(payload)
        return

    if stream == "trades":
        # Trades are heterogeneous (built / rendered / outcome). Show the most
        # informative summary fields.
        rows = []
        for r in records:
            d = r.get("data", {})
            phase = d.get("phase", "—")
            prop = d.get("proposal", {}) or {}
            v = d.get("validation") or {}
            rows.append({
                "ts": _fmt_ts(r["ts"]),
                "phase": phase,
                "symbol": prop.get("symbol"),
                "strategy": prop.get("strategy"),
                "exp": prop.get("expiration"),
                "credit": _round(prop.get("credit"), 2),
                "pop": _pct(prop.get("pop")),
                "rank": _round(prop.get("rank_score"), 2),
                "validation": v.get("valid"),
            })
        st.dataframe(rows, **WIDTH_STRETCH, hide_index=True)

        with st.expander("Inspect raw trade payloads"):
            idx = st.number_input(
                "Record index", min_value=0, max_value=len(records) - 1, value=0)
            st.json(records[int(idx)])
        return

    # events / fallback
    rows = []
    for r in records:
        d = r.get("data", {})
        rows.append({
            "ts": _fmt_ts(r["ts"]),
            "message": d.get("message"),
            "context": {k: v for k, v in d.items() if k != "message"},
        })
    st.dataframe(rows, **WIDTH_STRETCH, hide_index=True)


def _decision_summary(kind: str, payload: Dict[str, Any]) -> str:
    if kind == "regime":
        return (f"{payload.get('regime', '—')}  "
                f"deploy={payload.get('deploy')}")
    if kind == "validation":
        return (f"{payload.get('symbol', '—')} {payload.get('strategy', '')} "
                f"valid={payload.get('valid')}")
    return ""


def _fmt_ts(ts: str) -> str:
    try:
        return datetime.fromisoformat(ts).strftime("%H:%M:%S")
    except (ValueError, TypeError):
        return ts


def _round(x, n=2):
    if x is None:
        return None
    try:
        return round(float(x), n)
    except (TypeError, ValueError):
        return x


def _pct(x):
    if x is None:
        return None
    try:
        return f"{float(x):.0%}"
    except (TypeError, ValueError):
        return x


main()
