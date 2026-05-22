"""Trade Detail — full execution card, validation status, failure flags
for one selected proposal."""
from __future__ import annotations

from datetime import date
from typing import Optional

import streamlit as st

from options_system.dashboard.components import regime_banner, replay_banner, sidebar_controls
from options_system.dashboard.state import get_components
from options_system.dashboard.styling import WIDTH_STRETCH, PALETTE, configure_page
from options_system.execution import format_trade_card, suggested_limit_price
from options_system.failure_logic import evaluate_proposal
from options_system.trade_builder import TradeProposal
from options_system.validator import ValidationResult


def main() -> None:
    configure_page("Trade Detail", icon="📋")
    st.title("Trade Detail")
    st.caption("Execution-ready instructions, validation, failure-logic flags")

    run = sidebar_controls()
    replay_banner(run)
    regime_banner(run.regime)
    st.markdown("---")

    if not run.proposals:
        st.info("No proposals built today. Visit the **Today's Candidates** page.")
        return

    # --- selector ---
    default_idx = int(st.session_state.get("selected_proposal_index", 0))
    default_idx = min(default_idx, len(run.proposals) - 1)
    labels = [_proposal_label(p, i) for i, p in enumerate(run.proposals)]
    chosen_idx = st.selectbox(
        "Proposal", options=range(len(labels)),
        format_func=lambda i: labels[i],
        index=default_idx,
    )
    st.session_state["selected_proposal_index"] = chosen_idx
    proposal = run.proposals[chosen_idx]

    # Find or build a fresh validation. If we already validated this proposal
    # in the cached run, reuse it.
    validation = _matching_validation(run.validations, proposal)
    revalidate_col, _ = st.columns([1, 5])
    with revalidate_col:
        if st.button("🔁  Re-validate now", **WIDTH_STRETCH):
            with st.spinner("Refetching chain & re-validating…"):
                validator = get_components()["validator"]
                validation = validator.validate(proposal)

    # --- summary tiles ---
    cols = st.columns(4)
    with cols[0]:
        _tile("POP", f"{proposal.pop:.0%}")
    with cols[1]:
        _tile("Credit / Width",
              f"${proposal.credit:.2f} / ${proposal.width:.2f}",
              sub=f"ratio {proposal.credit_to_width_ratio:.0%}")
    with cols[2]:
        er_dir = "below" if proposal.m2m_flip_price < proposal.underlying_price else "above"
        _tile("Early-red M2M flip",
              f"${proposal.m2m_flip_price:.2f}",
              sub=f"{proposal.m2m_flip_distance_pct:.2%} {er_dir} spot · 5d / 25% loss")
    with cols[3]:
        _tile("Suggested limit", f"${suggested_limit_price(proposal):.2f}",
              sub=f"max loss ${proposal.max_loss:.2f}")

    # Secondary risk row — expiration breakeven + resilience.
    cols2 = st.columns(4)
    with cols2[0]:
        be_dir = "below" if proposal.expiration_breakeven_price < proposal.underlying_price else "above"
        _tile("Expiration breakeven",
              f"${proposal.expiration_breakeven_price:.2f}",
              sub=f"{proposal.expiration_breakeven_distance_pct:.2%} {be_dir} spot")
    with cols2[1]:
        _tile("Resilience score",
              f"{proposal.early_red_pl_score:.2f}",
              sub="spot+IV shocks, 5d window")
    with cols2[2]:
        _tile("Expected move (1σ)", f"${proposal.expected_move:.2f}",
              sub=f"ATR ${proposal.atr:.2f}")
    with cols2[3]:
        _tile("Max loss", f"${proposal.max_loss:.2f}",
              sub=f"credit ${proposal.credit:.2f} · width ${proposal.width:.2f}")

    # --- legs table ---
    st.markdown("### Legs")
    leg_rows = []
    for i, leg in enumerate(proposal.legs, 1):
        leg_rows.append({
            "#": i,
            "Action": leg.action,
            "Right": "Call" if leg.right.upper().startswith("C") else "Put",
            "Strike": f"${leg.strike:.2f}",
            "Expiration": leg.expiration.isoformat(),
            "Bid": f"{leg.bid:.2f}",
            "Ask": f"{leg.ask:.2f}",
            "Mid": f"{leg.mid:.2f}",
            "Δ": f"{leg.delta:+.2f}" if leg.delta is not None else "—",
            "IV": f"{leg.iv:.0%}" if leg.iv is not None else "—",
            "OCC": leg.contract_symbol or "—",
        })
    st.dataframe(leg_rows, hide_index=True, **WIDTH_STRETCH)

    # --- validation panel ---
    st.markdown("### Validation")
    if validation is None:
        st.info("Not yet validated. Click **Re-validate now** above.")
    else:
        if validation.valid:
            st.success("**VALID — OK to enter**")
        else:
            st.error("**INVALID — DO NOT ENTER**")
        for r in validation.reasons:
            st.markdown(f"- {r}")
        if validation.flags:
            with st.expander("Non-blocking warnings"):
                for f in validation.flags:
                    st.markdown(f"- {f}")
        meta_cols = st.columns(3)
        with meta_cols[0]:
            if validation.fresh_credit is not None:
                st.metric("Fresh credit", f"${validation.fresh_credit:.2f}")
        with meta_cols[1]:
            if validation.credit_drift_pct is not None:
                st.metric("Credit drift", f"{validation.credit_drift_pct:+.1%}")
        with meta_cols[2]:
            if validation.regime is not None:
                st.metric("Regime at validate", validation.regime.regime)

    # --- failure-logic flags ---
    st.markdown("### Failure-Logic Signals")
    sigs = evaluate_proposal(proposal)
    if not sigs:
        st.success("No pre-trade failure signals raised.")
    else:
        for sig in sigs:
            badge = {"REJECT": "🛑", "WARN": "⚠️", "INFO": "ℹ️"}.get(sig.severity, "•")
            st.markdown(f"{badge} **{sig.code}** — {sig.message}  *(`{sig.severity}`)*")
    if proposal.flags:
        st.caption(f"Builder flags: {', '.join(proposal.flags)}")

    # --- exit ladder ---
    st.markdown("### Management")
    exit_cols = st.columns(4)
    with exit_cols[0]:
        _tile("Take 50% off",
              f"${proposal.exit_50pct_target_credit:.2f}",
              sub=f"~{proposal.est_days_to_50pct} days")
    with exit_cols[1]:
        _tile("Scale 25% off",
              f"${proposal.exit_25pct_target_credit:.2f}",
              sub=f"~{proposal.est_days_to_25pct} days")
    with exit_cols[2]:
        _tile("Hard stop", "M2M flip breached",
              sub="or 2× credit loss")
    with exit_cols[3]:
        _tile("Time stop", "10 DTE", sub="close regardless of P/L")

    # --- ranking transparency ---
    with st.expander("Ranking breakdown"):
        st.markdown(f"**Total rank score: {proposal.rank_score:.2f}**")
        for r in proposal.rank_reasons:
            st.markdown(f"- {r}")

    # --- full text card ---
    with st.expander("📋  Copy-paste trade card (text)"):
        st.code(format_trade_card(proposal, validation, contracts=1),
                language="text")


def _proposal_label(p: TradeProposal, idx: int) -> str:
    return (f"#{idx + 1:>2}  {p.symbol:<5}  {p.strategy:<11}  "
            f"K {p.short_strike:>7.2f}  exp {p.expiration}  "
            f"credit ${p.credit:.2f}  POP {p.pop:.0%}")


def _matching_validation(validations, proposal) -> Optional[ValidationResult]:
    for v in validations:
        if (v.proposal.symbol == proposal.symbol
                and v.proposal.strategy == proposal.strategy
                and v.proposal.expiration == proposal.expiration
                and v.proposal.short_strike == proposal.short_strike):
            return v
    return None


def _tile(label: str, value: str, sub: str = "") -> None:
    sub_html = f"<div class='delta'>{sub}</div>" if sub else ""
    st.markdown(
        f"<div class='metric-card'>"
        f"<div class='label'>{label}</div>"
        f"<div class='value'>{value}</div>{sub_html}</div>",
        unsafe_allow_html=True,
    )


main()
