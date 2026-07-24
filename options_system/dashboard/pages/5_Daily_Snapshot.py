"""Daily Snapshot — single plain-text dump of today's pipeline output.

Built for the case where the client wants to paste the system's daily
output into an outside AI advisor (Chat, ChatGPT, Claude). Streamlit
URLs don't browse well in ChatGPT (the page is rendered by JavaScript
so the text isn't in the raw HTML), but a single copyable code block
on this page renders cleanly and is easy to paste.

This page is also useful as a one-screen status check.
"""
from __future__ import annotations

# --- Streamlit Cloud path fix (see options_system/dashboard/app.py for context) ---
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from datetime import date, datetime
from typing import List

import streamlit as st

from options_system.dashboard.components import replay_banner, sidebar_controls
from options_system.dashboard.state import PipelineRun
from options_system.dashboard.styling import configure_page
from options_system.trade_builder import TradeProposal
from options_system.validator import ValidationResult


def main() -> None:
    configure_page("Daily Snapshot", icon="📋")
    st.title("Daily Snapshot")
    st.caption(
        "Plain-text dump of today's pipeline output. Copy the whole block and "
        "paste it into your AI advisor for full system context."
    )

    run = sidebar_controls()
    replay_banner(run)
    st.markdown("---")

    if run.error:
        st.warning(
            f"Live data fetch is currently failing: {run.error}\n\n"
            "Yahoo Finance occasionally rate-limits or returns malformed "
            "responses. Try Refresh in a minute, or use Replay mode on a "
            "past date to see populated output."
        )

    snapshot = build_snapshot(run)

    st.markdown("### Copy and paste into your AI advisor")
    st.code(snapshot, language="markdown")

    st.markdown("---")
    st.caption(
        "Note: This snapshot represents what the system saw at the time of the "
        "latest pipeline run. Refresh from the sidebar for a fresh run. The "
        "README at the root of the GitHub repo describes the full system in "
        "more detail and is also worth pasting into your advisor."
    )


def build_snapshot(run: PipelineRun) -> str:
    """Render the run as a single self-contained markdown blob."""
    lines: List[str] = []
    ts = run.run_at.strftime("%Y-%m-%d %H:%M UTC")
    mode = f"Replay {run.replay_date.isoformat()}" if run.replay_date else "Live"
    lines.append("# Grant Options Income System — Daily Snapshot")
    lines.append("")
    lines.append(f"Mode: {mode}")
    lines.append(f"Run time: {ts}")
    lines.append(f"Stages completed: {' -> '.join(run.stages_completed) or 'none'}")
    if run.error:
        lines.append(f"Pipeline error: {run.error}")
    lines.append("")

    # Regime section
    lines.append("## Regime")
    if run.regime is None:
        lines.append("Regime not yet evaluated.")
    else:
        r = run.regime
        deploy = "DEPLOY" if r.deploy else "NO-TRADE"
        lines.append(f"Label: {r.regime}")
        lines.append(f"Decision: {deploy}")
        lines.append(f"Size multiplier: {r.size_mult:.2f}")
        lines.append("Reasoning:")
        for reason in r.reasons:
            lines.append(f"  - {reason}")
        if r.metrics:
            lines.append("Key metrics:")
            for k, v in r.metrics.items():
                if isinstance(v, float):
                    lines.append(f"  - {k}: {v:.4f}")
                else:
                    lines.append(f"  - {k}: {v}")
    lines.append("")

    # Candidates
    lines.append("## Candidates")
    if not run.candidates:
        lines.append("No candidates passed scanner filters.")
    else:
        lines.append(f"{len(run.candidates)} ticker(s) passed scanner filters.")
        lines.append("")
        for c in run.candidates:
            lines.append(f"### {c.symbol}")
            lines.append(f"  Quality score: {c.quality_score:.2f}")
            lines.append(f"  Underlying price: ${c.underlying_price:.2f}")
            lines.append(f"  Near-ATM IV: {c.avg_iv:.1%}")
            if c.iv_rank is not None:
                lines.append(f"  IV-rank proxy: {c.iv_rank:.2f}")
            lines.append(f"  ATR: ${c.atr:.2f}")
            if c.atr_compression_ratio is not None:
                lines.append(f"  ATR compression ratio: {c.atr_compression_ratio:.2f}")
            if c.bb_width_compression_ratio is not None:
                lines.append(f"  BB width compression ratio: {c.bb_width_compression_ratio:.2f}")
            exps = ", ".join(d.isoformat() for d in c.expirations_in_window)
            lines.append(f"  Expirations in DTE window: {exps}")
            lines.append(f"  Index product: {c.is_index_product}")
            lines.append("")

    # Proposals
    lines.append("## Trade Proposals")
    if not run.proposals:
        lines.append("No proposals built today.")
    else:
        val_lookup = {
            (v.proposal.symbol, v.proposal.strategy, v.proposal.expiration,
             v.proposal.short_strike): v for v in run.validations
        }
        lines.append(f"{len(run.proposals)} proposal(s) built. Top {min(10, len(run.proposals))} below.")
        lines.append("")
        for idx, p in enumerate(run.proposals[:10], 1):
            v = val_lookup.get((p.symbol, p.strategy, p.expiration, p.short_strike))
            lines.extend(_render_proposal(idx, p, v))
            lines.append("")

    # Phase 1.5 context for the advisor
    lines.append("## System Notes")
    lines.append(
        "Risk numbers above reflect Phase 1.5 definitions:"
    )
    lines.append(
        "- Early-red M2M flip: underlying price where, 5 days from entry, "
        "M2M loss equals 25% of credit. Path-aware risk threshold."
    )
    lines.append(
        "- Expiration breakeven: short strike plus or minus credit. "
        "Textbook breakeven, shown as secondary reference only."
    )
    lines.append(
        "- Resilience score: 0 to 1, fraction of ~60 stress scenarios "
        "(spot shocks x IV shocks x days 1-5) where the trade stays not-red."
    )
    lines.append(
        "- POP is approximated as 1 minus absolute delta of the short leg."
    )
    lines.append(
        "- All thresholds live in YAML configs and are tunable without code changes."
    )
    lines.append("")
    lines.append(
        "See README.md at the root of the GitHub repo for full system documentation."
    )

    return "\n".join(lines)


def _render_proposal(idx: int, p: TradeProposal,
                     v: ValidationResult | None) -> List[str]:
    lines: List[str] = []
    dte = (p.expiration - date.today()).days
    lines.append(f"### #{idx}: {p.symbol} {p.strategy} exp {p.expiration} ({dte} DTE)")
    lines.append(f"  Mode: {p.mode.upper()}")
    if p.score_card:
        lines.append(f"  Overall score: {p.score_card.get('Overall', 0)}/100  "
                     f"({', '.join(f'{k} {v}' for k, v in p.score_card.items() if k != 'Overall')})")

    # Legs
    for leg in p.legs:
        right = "Call" if leg.right.upper().startswith("C") else "Put"
        delta = f"{leg.delta:+.2f}" if leg.delta is not None else "n/a"
        lines.append(
            f"  Leg: {leg.action} {right} ${leg.strike:.2f}  "
            f"bid {leg.bid:.2f} / ask {leg.ask:.2f} / mid {leg.mid:.2f}  "
            f"delta {delta}"
        )

    # Order
    lines.append(f"  Underlying spot: ${p.underlying_price:.2f}")
    lines.append(f"  Credit: ${p.credit:.2f}  Width: ${p.width:.2f}  "
                 f"Max loss: ${p.max_loss:.2f}")
    lines.append(f"  Credit/width ratio: {p.credit_to_width_ratio:.0%}")
    lines.append(f"  POP: {p.pop:.0%}")

    # Risk
    er_dir = "below" if p.m2m_flip_price < p.underlying_price else "above"
    be_dir = ("below" if p.expiration_breakeven_price < p.underlying_price
              else "above")
    lines.append(
        f"  Early-red M2M flip: ${p.m2m_flip_price:.2f} "
        f"({p.m2m_flip_distance_pct:.2%} {er_dir} spot, 5d/25% loss)"
    )
    lines.append(
        f"  Expiration breakeven: ${p.expiration_breakeven_price:.2f} "
        f"({p.expiration_breakeven_distance_pct:.2%} {be_dir} spot)"
    )
    lines.append(f"  Expected move (1 sigma): ${p.expected_move:.2f}")
    lines.append(f"  ATR: ${p.atr:.2f}")
    lines.append(f"  Resilience score: {p.early_red_pl_score:.2f}")

    # Exits
    lines.append(
        f"  50% profit target: buy back at ${p.exit_50pct_target_credit:.2f} "
        f"(~{p.est_days_to_50pct}d)"
    )
    lines.append(
        f"  25% profit target: buy back at ${p.exit_25pct_target_credit:.2f} "
        f"(~{p.est_days_to_25pct}d)"
    )

    # Flags
    if p.flags:
        lines.append(f"  Flags: {', '.join(p.flags)}")
    lines.append(f"  Rank score: {p.rank_score:.2f}")

    # Validation
    if v is None:
        lines.append("  Validation: not run yet")
    elif v.valid:
        lines.append("  Validation: VALID (OK to enter)")
        if v.credit_drift_pct is not None:
            lines.append(f"  Credit drift since build: {v.credit_drift_pct:+.1%}")
        if v.flags:
            lines.append(f"  Non-blocking warnings: {'; '.join(v.flags)}")
    else:
        lines.append("  Validation: INVALID (DO NOT ENTER)")
        for r in v.reasons:
            lines.append(f"    - {r}")

    return lines


main()
