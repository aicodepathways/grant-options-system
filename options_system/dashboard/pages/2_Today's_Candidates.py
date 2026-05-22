"""Today's Candidates — ranked table of trade proposals with strikes,
credit, POP, M2M distance, exit levels. Color-coded by rank."""
from __future__ import annotations

from datetime import date
from typing import List

import pandas as pd
import streamlit as st

from options_system.dashboard.components import regime_banner, replay_banner, sidebar_controls
from options_system.dashboard.styling import WIDTH_STRETCH, PALETTE, configure_page, rank_color
from options_system.trade_builder import TradeProposal


def main() -> None:
    configure_page("Today's Candidates", icon="🎯")
    st.title("Today's Candidates")
    st.caption("Ranked premium-selling proposals with risk and exit levels")

    run = sidebar_controls()
    replay_banner(run)
    regime_banner(run.regime)
    st.markdown("---")

    if run.regime is None or not run.regime.deploy:
        st.error(
            "**NO-TRADE day.** No proposals are surfaced when the regime gate "
            "is closed. Use *Force deploy* in the sidebar for research-only mode."
        )
        return

    proposals = run.proposals
    if not proposals:
        st.info("No proposals built today. Check the **Regime Overview** page.")
        return

    # Build a flat dataframe for display.
    df = _proposals_to_dataframe(proposals)

    # Status column from validation results (if any).
    val_by_key = {
        (v.proposal.symbol, v.proposal.strategy, v.proposal.expiration, v.proposal.short_strike): v
        for v in run.validations
    }
    statuses, validation_notes = [], []
    for p in proposals:
        v = val_by_key.get((p.symbol, p.strategy, p.expiration, p.short_strike))
        if v is None:
            statuses.append("—")
            validation_notes.append("not validated")
        elif v.valid:
            statuses.append("✅ VALID")
            validation_notes.append("; ".join(v.flags) or "all checks passed")
        else:
            statuses.append("🛑 INVALID")
            validation_notes.append("; ".join(v.reasons) or "rejected")
    df["Status"] = statuses
    df["Validation"] = validation_notes

    # Filters.
    filt_cols = st.columns([1, 1, 1, 2])
    with filt_cols[0]:
        only_valid = st.checkbox("Only VALID", value=False)
    with filt_cols[1]:
        strategy_filter = st.multiselect(
            "Strategy", df["Strategy"].unique().tolist(), default=[],
            placeholder="All",
        )
    with filt_cols[2]:
        symbols = sorted(df["Symbol"].unique().tolist())
        symbol_filter = st.multiselect("Symbol", symbols, default=[],
                                       placeholder="All")

    view = df.copy()
    if only_valid:
        view = view[view["Status"] == "✅ VALID"]
    if strategy_filter:
        view = view[view["Strategy"].isin(strategy_filter)]
    if symbol_filter:
        view = view[view["Symbol"].isin(symbol_filter)]

    if view.empty:
        st.warning("No proposals match the active filters.")
        return

    # Color-coded styled table.
    styled = view.style.apply(
        _row_color, total=len(view), axis=1
    ).format({
        "Credit": "${:.2f}", "Width": "${:.2f}", "Max Loss": "${:.2f}",
        "POP": "{:.0%}", "C/W": "{:.0%}",
        "Early-red flip $": "${:.2f}", "Early-red flip %": "{:.2%}",
        "Exp BE $": "${:.2f}", "Exp BE %": "{:.2%}",
        "Spot": "${:.2f}", "Rank": "{:.2f}",
        "50% target": "${:.2f}", "25% target": "${:.2f}",
    })

    st.dataframe(
        styled,
        **WIDTH_STRETCH,
        hide_index=True,
        height=min(60 + 36 * len(view), 720),
        column_config={
            "DTE": st.column_config.NumberColumn("DTE", width="small"),
            "POP": st.column_config.ProgressColumn(
                "POP", min_value=0, max_value=1, format="%.0f%%"),
            "Rank": st.column_config.NumberColumn("Rank", format="%.2f"),
            "Flags": st.column_config.TextColumn("Flags", width="medium"),
        },
    )

    # Trade-detail jump-off: encode the chosen rank in session state so the
    # Trade Detail page picks it up.
    st.markdown("### Open a Trade Card")
    pick_cols = st.columns([2, 1])
    with pick_cols[0]:
        labels = [_proposal_label(p, i) for i, p in enumerate(proposals)]
        choice = st.selectbox(
            "Select a proposal", options=range(len(labels)),
            format_func=lambda i: labels[i],
        )
    with pick_cols[1]:
        if st.button("Open in Trade Detail →", **WIDTH_STRETCH):
            st.session_state["selected_proposal_index"] = choice
            st.switch_page("pages/3_Trade_Detail.py")


def _proposals_to_dataframe(proposals: List[TradeProposal]) -> pd.DataFrame:
    today = date.today()
    rows = []
    for i, p in enumerate(proposals):
        rows.append({
            "Rank #": i + 1,
            "Symbol": p.symbol,
            "Strategy": p.strategy,
            "Expiration": p.expiration.isoformat(),
            "DTE": (p.expiration - today).days,
            "Spot": p.underlying_price,
            "Short K": p.short_strike,
            "Credit": p.credit,
            "Width": p.width,
            "Max Loss": p.max_loss,
            "C/W": p.credit_to_width_ratio,
            "POP": p.pop,
            "Early-red flip $": p.m2m_flip_price,
            "Early-red flip %": p.m2m_flip_distance_pct,
            "Exp BE $": p.expiration_breakeven_price,
            "Exp BE %": p.expiration_breakeven_distance_pct,
            "Resilience": round(p.early_red_pl_score, 2),
            "50% target": p.exit_50pct_target_credit,
            "25% target": p.exit_25pct_target_credit,
            "Flags": ", ".join(p.flags) if p.flags else "",
            "Rank": p.rank_score,
        })
    return pd.DataFrame(rows)


def _row_color(row: pd.Series, total: int):
    """Apply rank-based background color across the entire row.

    We set both background AND text color explicitly so the cells stay
    readable even when the user's OS / Streamlit theme is dark-mode.
    """
    rank_idx = row.name  # 0-indexed dataframe position
    bg = rank_color(rank_idx, total)
    return [f"background-color: {bg}; color: #1f2329"] * len(row)


def _proposal_label(p: TradeProposal, idx: int) -> str:
    return (f"#{idx + 1:>2}  {p.symbol:<5}  {p.strategy:<11}  "
            f"K {p.short_strike:>7.2f}  exp {p.expiration}  "
            f"credit ${p.credit:.2f}  POP {p.pop:.0%}")


main()
