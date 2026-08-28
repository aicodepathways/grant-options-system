"""Publish the daily pipeline snapshot as plain files for AI-advisor ingestion.

Runs the same pipeline as the dashboard (regime -> scan -> build -> validate)
and writes:
    docs/daily_snapshot.md     human/AI readable markdown
    docs/daily_snapshot.json   structured version of the same data

A GitHub Action runs this every weekday morning and commits the result, so
the client's AI advisor can fetch a stable raw URL each day:
    https://raw.githubusercontent.com/aicodepathways/grant-options-system/main/docs/daily_snapshot.md

No Streamlit dependency — this must run headless on a CI runner.
Exit code 1 on total data failure so the workflow shows red instead of
silently committing an empty snapshot.
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import date, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
for noisy in ("yfinance", "peewee", "urllib3", "requests", "curl_cffi"):
    logging.getLogger(noisy).setLevel(logging.WARNING)
logger = logging.getLogger("publish_snapshot")

DOCS = REPO_ROOT / "docs"


def warmup_data(adapter, min_coverage: float = 0.70,
                rounds: int = 3, round_sleep: int = 20) -> None:
    """Pre-fetch history for every symbol the pipeline needs, retrying the
    failures across multiple rounds.

    Two jobs: (1) hammer Yahoo until enough of the universe actually
    responds — each round retries only what failed, and the successes land
    in the adapter's cache so the scanner reuses them without refetching;
    (2) hard-fail the run when coverage is too thin, so a Yahoo-blocked
    runner produces a failed job (which the workflow retries on a fresh
    machine with a fresh IP) instead of publishing a hollow snapshot that
    says "no candidates today" when the truth is "no data today."

    Raises RuntimeError if the regime symbols fail or coverage stays below
    `min_coverage` after all rounds.
    """
    import time as _time

    from options_system.config import load_config

    u = load_config("scanner_config").get("universe", {}) or {}
    universe = list(u.get("index_etfs", [])) + list(u.get("equities", []))
    spx = getattr(adapter, "SPX_SYMBOL", "^GSPC")
    vix = getattr(adapter, "VIX_SYMBOL", "^VIX")

    # Regime inputs are non-negotiable — retry them within each round via
    # the adapter's own retry logic, and fail the run if they never load.
    regime_ok = False
    pending = set(universe)
    for rnd in range(1, rounds + 1):
        if not regime_ok:
            try:
                adapter.get_history(spx, period="6mo")
                adapter.get_vix_history(period="3mo")
                adapter.get_vix()
                regime_ok = True
            except Exception as exc:
                logger.warning("warmup round %d: regime data failed: %s", rnd, exc)

        for sym in sorted(pending):
            try:
                adapter.get_history(sym, period="6mo")
                pending.discard(sym)
            except Exception as exc:
                logger.warning("warmup round %d: %s failed: %s", rnd, sym, exc)

        coverage = 1.0 - (len(pending) / max(len(universe), 1))
        logger.info("warmup round %d: regime_ok=%s coverage=%.0f%% (%d/%d tickers)",
                    rnd, regime_ok, coverage * 100,
                    len(universe) - len(pending), len(universe))
        if regime_ok and coverage >= min_coverage:
            return
        if rnd < rounds:
            _time.sleep(round_sleep)

    if not regime_ok:
        raise RuntimeError(
            "Yahoo refused the regime inputs (SPX/VIX) after "
            f"{rounds} warmup rounds — data source unavailable from this host"
        )
    coverage = 1.0 - (len(pending) / max(len(universe), 1))
    raise RuntimeError(
        f"universe data coverage {coverage:.0%} below required "
        f"{min_coverage:.0%} after {rounds} warmup rounds "
        f"(missing: {', '.join(sorted(pending))})"
    )


def run_pipeline():
    from options_system.data import get_adapter
    from options_system.regime_engine import RegimeEngine
    from options_system.scanner import Scanner
    from options_system.trade_builder import TradeBuilder
    from options_system.validator import Validator

    adapter = get_adapter()
    warmup_data(adapter)
    regime_engine = RegimeEngine(adapter)
    scanner = Scanner(adapter)
    builder = TradeBuilder(adapter)
    validator = Validator(adapter, regime_engine)

    regime = regime_engine.evaluate()
    candidates, proposals, validations = [], [], []
    if regime.deploy:
        candidates = scanner.scan()
        if candidates:
            proposals = builder.build_for_candidates(candidates, top_n_per=2)
            for p in proposals[:5]:
                try:
                    validations.append(validator.validate(p))
                except Exception as exc:
                    logger.warning("validation failed for %s: %s", p.symbol, exc)
    return regime, candidates, proposals, validations


def render_markdown(regime, candidates, proposals, validations) -> str:
    # Pacific time in the header because the client reads in Pacific.
    # Zoneinfo handles PDT/PST automatically.
    try:
        from zoneinfo import ZoneInfo
        now_pt = datetime.now(ZoneInfo("America/Los_Angeles"))
        pt_str = f"{now_pt:%A, %B %d, %Y at %I:%M %p} Pacific"
    except Exception:
        pt_str = "unavailable"

    lines = []
    lines.append("# Grant Options Income System — Daily Snapshot")
    lines.append("")
    lines.append(f"Generated: {datetime.utcnow():%Y-%m-%d %H:%M} UTC (live data)")
    lines.append(f"Generated (Pacific): {pt_str}")
    lines.append("")
    lines.append("Freshness note for the reader: this page refreshes several "
                 "times each weekday morning, roughly 6:45 AM to noon Pacific. "
                 "Exact times drift because the free scheduler queues jobs. "
                 "If the date above is not today, today's first run has not "
                 "completed yet; advise re-checking after 7:30 AM Pacific "
                 "rather than treating it as a failure.")
    lines.append("")
    lines.append("## Regime")
    lines.append(f"Label: {regime.regime}")
    lines.append(f"Decision: {'DEPLOY' if regime.deploy else 'NO-TRADE'}")
    lines.append(f"Size multiplier: {regime.size_mult:.2f}")
    for r in regime.reasons:
        lines.append(f"  - {r}")
    lines.append("")

    lines.append("## Candidates")
    if not candidates:
        lines.append("No candidates passed scanner filters today.")
    else:
        for c in candidates:
            lines.append(
                f"- {c.symbol}: score {c.quality_score:.2f}, "
                f"spot ${c.underlying_price:.2f}, near-ATM IV {c.avg_iv:.1%}, "
                f"ATR ${c.atr:.2f}"
            )
    lines.append("")

    lines.append("## Trade Proposals")
    if not proposals:
        lines.append("No proposals built today.")
    else:
        val_lookup = {
            (v.proposal.symbol, v.proposal.strategy, v.proposal.expiration,
             v.proposal.short_strike): v for v in validations
        }
        for i, p in enumerate(proposals[:10], 1):
            dte = (p.expiration - date.today()).days
            lines.append(f"### #{i}: {p.symbol} {p.strategy} exp {p.expiration} ({dte} DTE)")
            lines.append(f"  Mode: {p.mode.upper()}")
            if p.score_card:
                detail = ", ".join(f"{k} {v}" for k, v in p.score_card.items()
                                   if k != "Overall")
                lines.append(f"  Overall score: {p.score_card.get('Overall', 0)}/100 ({detail})")
            for leg in p.legs:
                right = "Call" if leg.right.upper().startswith("C") else "Put"
                lines.append(f"  Leg: {leg.action} {right} ${leg.strike:.2f} mid {leg.mid:.2f}")
            lines.append(f"  Spot ${p.underlying_price:.2f}  Credit ${p.credit:.2f}  "
                         f"Width ${p.width:.2f}  POP {p.pop:.0%}")
            er_dir = "below" if p.m2m_flip_price < p.underlying_price else "above"
            lines.append(f"  Early-red M2M flip: ${p.m2m_flip_price:.2f} "
                         f"({p.m2m_flip_distance_pct:.2%} {er_dir} spot)")
            lines.append(f"  Expiration breakeven: ${p.expiration_breakeven_price:.2f}  "
                         f"Resilience: {p.early_red_pl_score:.2f}")
            lines.append(f"  Exits: 50% at ${p.exit_50pct_target_credit:.2f}, "
                         f"25% at ${p.exit_25pct_target_credit:.2f}")
            v = val_lookup.get((p.symbol, p.strategy, p.expiration, p.short_strike))
            if v is None:
                lines.append("  Validation: not run")
            elif v.valid:
                lines.append("  Validation: VALID")
            else:
                lines.append(f"  Validation: INVALID ({'; '.join(v.reasons)})")
            if p.flags:
                lines.append(f"  Flags: {', '.join(p.flags)}")
            lines.append("")

    lines.append("## Notes for the AI advisor")
    lines.append("- INCOME mode = conservative spec (wide strikes, 70-90% POP).")
    lines.append("- OPPORTUNITY mode = the client's low-vol SPX style "
                 "(strikes near half the expected move, credit 30-50% of width, "
                 "POP floor ~55%). Index products only, VIX under 18.")
    lines.append("- Early-red M2M flip = price where the trade is down 25% of "
                 "credit 5 days after entry. The primary risk number.")
    lines.append("- Full system documentation: README.md at the repo root.")
    return "\n".join(lines)


def render_html(md: str) -> str:
    """Wrap the markdown snapshot in minimal static HTML.

    Deliberately no JavaScript and no styling beyond a monospace block:
    the audience is an AI advisor's web fetcher, which needs the text in
    the raw HTML response body.
    """
    import html as _html
    return (
        "<!DOCTYPE html>\n<html><head><meta charset='utf-8'>"
        "<title>Grant Options System - Daily Snapshot</title></head>"
        "<body><pre>\n"
        + _html.escape(md)
        + "\n</pre></body></html>\n"
    )


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    try:
        regime, candidates, proposals, validations = run_pipeline()
    except Exception as exc:
        logger.error("pipeline failed: %s", exc)
        # Leave the previous snapshot in place; write a status marker so the
        # advisor knows today's run failed rather than silently reading
        # yesterday's data as today's.
        marker = (
            f"# Snapshot update FAILED\n\n"
            f"Attempted: {datetime.utcnow():%Y-%m-%d %H:%M} UTC\n"
            f"Error: {exc}\n\n"
            f"The snapshot below this notice (daily_snapshot.md) is from a "
            f"previous successful run.\n"
        )
        (DOCS / "last_run_status.md").write_text(marker)
        return 1

    md = render_markdown(regime, candidates, proposals, validations)
    (DOCS / "daily_snapshot.md").write_text(md)
    # .txt alias — served as text/plain by Pages, the friendliest possible
    # content type for AI fetchers that struggle with markdown or HTML.
    (DOCS / "daily_snapshot.txt").write_text(md)
    # HTML twin served via GitHub Pages. ChatGPT's browsing tool often
    # fails on raw.githubusercontent.com but reads normal *.github.io
    # pages fine, so this is the URL the client's AI advisor uses:
    #   https://aicodepathways.github.io/grant-options-system/
    (DOCS / "index.html").write_text(render_html(md))
    (DOCS / "daily_snapshot.json").write_text(json.dumps({
        "generated_utc": datetime.utcnow().isoformat(),
        "regime": regime.to_dict(),
        "candidates": [c.to_dict() for c in candidates],
        "proposals": [p.to_dict() for p in proposals[:10]],
        "validations": [v.to_dict() for v in validations],
    }, indent=2, default=str))
    (DOCS / "last_run_status.md").write_text(
        f"# Snapshot updated successfully\n\n"
        f"Generated: {datetime.utcnow():%Y-%m-%d %H:%M} UTC\n")
    logger.info("snapshot written: %d candidates, %d proposals",
                len(candidates), len(proposals))
    return 0


if __name__ == "__main__":
    sys.exit(main())
