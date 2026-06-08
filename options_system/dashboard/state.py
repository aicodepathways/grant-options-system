"""Shared dashboard state — pipeline runs are cached for the session so
clicking between pages doesn't re-hit yfinance.

The cache key is the run timestamp; the user can force a refresh from the
sidebar. This keeps the live data adapter's cache TTL doing its job
underneath while making the UI snappy.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import List, Optional

import streamlit as st

from ..data import get_adapter
from ..logging_system import DailyLogger
from ..regime_engine import RegimeEngine, RegimeReading
from ..scanner import Candidate, Scanner
from ..trade_builder import TradeBuilder, TradeProposal
from ..validator import ValidationResult, Validator

logger = logging.getLogger(__name__)


@dataclass
class PipelineRun:
    run_at: datetime
    regime: Optional[RegimeReading] = None
    candidates: List[Candidate] = field(default_factory=list)
    proposals: List[TradeProposal] = field(default_factory=list)
    validations: List[ValidationResult] = field(default_factory=list)
    error: Optional[str] = None
    # How far the pipeline got. Useful when an exception cuts a run short.
    stages_completed: List[str] = field(default_factory=list)
    # When set, this run reflects a historical replay (BacktestAdapter), not
    # the live market — pages should annotate that to the user.
    replay_date: Optional[date] = None


def _empty_run() -> PipelineRun:
    return PipelineRun(run_at=datetime.utcnow())


@st.cache_resource(show_spinner=False)
def get_components():
    """Singletons — created once per Streamlit process."""
    adapter = get_adapter()
    regime_engine = RegimeEngine(adapter)
    scanner = Scanner(adapter)
    builder = TradeBuilder(adapter)
    validator = Validator(adapter, regime_engine)
    return {
        "adapter": adapter,
        "regime_engine": regime_engine,
        "scanner": scanner,
        "builder": builder,
        "validator": validator,
    }


def run_pipeline(top_n: int = 5, force_deploy: bool = False,
                 skip_validation: bool = False) -> PipelineRun:
    """Execute the same pipeline as `main.py` and return the result bundle.

    Side-effect: appends to the daily JSONL streams so the Log Viewer page
    has fresh data after each refresh.
    """
    run = _empty_run()
    comps = get_components()
    daily = DailyLogger()
    daily.log_event("dashboard_run_started",
                    top_n=top_n, force_deploy=force_deploy,
                    skip_validation=skip_validation)
    try:
        run.regime = comps["regime_engine"].evaluate()
        daily.log_decision("regime", run.regime)
        run.stages_completed.append("regime")

        if not run.regime.deploy and not force_deploy:
            daily.log_event("no_trade", reason=run.regime.regime)
            return run

        run.candidates = comps["scanner"].scan()
        daily.log_candidates(run.candidates)
        run.stages_completed.append("scan")

        if not run.candidates:
            daily.log_event("no_candidates")
            return run

        run.proposals = comps["builder"].build_for_candidates(
            run.candidates, top_n_per=2)
        for p in run.proposals:
            daily.log_trade({"phase": "built", "proposal": p.to_dict()})
        run.stages_completed.append("build")

        if not run.proposals:
            return run

        if not skip_validation:
            for p in run.proposals[:top_n]:
                try:
                    v = comps["validator"].validate(p)
                except Exception as exc:
                    logger.warning("validation failed for %s: %s", p.symbol, exc)
                    continue
                run.validations.append(v)
                daily.log_decision("validation", v)
            run.stages_completed.append("validate")

    except Exception as exc:
        logger.exception("pipeline run failed")
        daily.log_event("pipeline error", error=str(exc))
        run.error = str(exc)
    finally:
        daily.log_event("dashboard_run_finished", counts=daily.counts())
    return run


def run_replay_pipeline(replay_date: date, top_n: int = 5,
                        force_deploy: bool = False,
                        skip_validation: bool = False) -> PipelineRun:
    """Run the same pipeline against the BacktestAdapter set to `replay_date`.

    Useful for showing the dashboard populated with realistic candidates on
    a past date when today's regime + vol won't surface any. Synthetic
    chains apply — IVs are realized-vol proxies, no skew. The same code
    paths as live run, just a different data adapter.
    """
    from ..backtester import BacktestAdapter

    run = _empty_run()
    run.replay_date = replay_date
    try:
        adapter = BacktestAdapter()
        adapter.set_as_of(replay_date)
        regime_engine = RegimeEngine(adapter)
        scanner = Scanner(adapter)
        builder = TradeBuilder(adapter)
        validator = Validator(adapter, regime_engine)

        run.regime = regime_engine.evaluate()
        run.stages_completed.append("regime")

        if not run.regime.deploy and not force_deploy:
            return run

        run.candidates = scanner.scan()
        run.stages_completed.append("scan")
        if not run.candidates:
            return run

        run.proposals = builder.build_for_candidates(run.candidates, top_n_per=2)
        run.stages_completed.append("build")
        if not run.proposals:
            return run

        if not skip_validation:
            for p in run.proposals[:top_n]:
                try:
                    v = validator.validate(p)
                except Exception as exc:
                    logger.warning("replay validation failed for %s: %s", p.symbol, exc)
                    continue
                run.validations.append(v)
            run.stages_completed.append("validate")

    except Exception as exc:
        logger.exception("replay pipeline failed")
        run.error = str(exc)
    return run


def get_or_create_run(force_refresh: bool = False,
                      replay_date: Optional[date] = None,
                      **kwargs) -> PipelineRun:
    """Session-cached pipeline run. Sidebar `Refresh` flips force_refresh.

    Cache key includes the replay date so flipping between live and replay
    (or between replay dates) doesn't smash a previously-fetched run.
    """
    key = f"pipeline_run::{replay_date.isoformat() if replay_date else 'live'}"
    if force_refresh or key not in st.session_state:
        with st.spinner(
            f"Running pipeline ({'replay ' + replay_date.isoformat() if replay_date else 'live'}) "
            "(regime → scan → build → validate)…"
        ):
            if replay_date is not None:
                st.session_state[key] = run_replay_pipeline(
                    replay_date=replay_date, **kwargs)
            else:
                st.session_state[key] = run_pipeline(**kwargs)
    return st.session_state[key]
