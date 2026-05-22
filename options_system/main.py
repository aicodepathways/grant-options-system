"""Daily workflow orchestrator.

Pipeline:
    regime_engine.evaluate()                         # gate
    └── if DEPLOY:
        scanner.scan()                                # candidates
        └── trade_builder.build_for_candidates(...)   # proposals
            └── validator.validate(p) for top N       # VALID/INVALID
                └── execution.format_trade_card(p)    # user-facing output

Everything is logged via DailyLogger. The CLI flags below allow dry-run
inspection (no validator pass), forcing a deploy, or limiting top-N output.

Usage:
    python -m options_system.main
    python -m options_system.main --top 3 --no-validate
    python -m options_system.main --backtest 2024-01-01 2024-06-30
"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import date, datetime
from typing import List

from .config import load_config
from .data import get_adapter
from .execution import format_trade_card
from .logging_system import DailyLogger, daily_summary
from .regime_engine import RegimeEngine
from .scanner import Scanner
from .trade_builder import TradeBuilder
from .validator import Validator


def _setup_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
    )
    # yfinance + peewee + urllib3 are extremely chatty at DEBUG; pin them to WARNING
    # so our verbose output stays useful.
    for noisy in ("yfinance", "peewee", "urllib3", "requests", "curl_cffi"):
        logging.getLogger(noisy).setLevel(logging.WARNING)


def _parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def _argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="options_system",
                                description="Daily premium-selling pipeline")
    p.add_argument("--top", type=int, default=5,
                   help="how many proposals to fully validate and render")
    p.add_argument("--no-validate", action="store_true",
                   help="skip the real-time validator pass")
    p.add_argument("--force-deploy", action="store_true",
                   help="ignore the regime gate (research mode only)")
    p.add_argument("--verbose", "-v", action="store_true")
    p.add_argument("--backtest", nargs=2, metavar=("START", "END"),
                   help="run a backtest START..END (YYYY-MM-DD) instead of live")
    return p


def run_live(args: argparse.Namespace) -> int:
    daily_log = DailyLogger()
    daily_log.log_event("run_started", mode="live")

    adapter = get_adapter()
    regime_engine = RegimeEngine(adapter)
    scanner = Scanner(adapter)
    builder = TradeBuilder(adapter)
    validator = Validator(adapter, regime_engine)

    # 1. Regime gate.
    regime = regime_engine.evaluate()
    daily_log.log_decision("regime", regime)
    print(f"[regime] {regime.regime}  deploy={regime.deploy}  "
          f"size_mult={regime.size_mult}")
    for r in regime.reasons:
        print(f"  - {r}")

    if not regime.deploy and not args.force_deploy:
        daily_log.log_event("no_trade", reason=regime.regime)
        print(f"\n>>> NO-TRADE day ({regime.regime}). Pipeline halted at regime gate.")
        print(daily_summary(daily_log, regime, [], [], []))
        return 0

    if not regime.deploy and args.force_deploy:
        print("\n[!!] --force-deploy set; continuing despite NO-TRADE regime.")

    # 2. Scan.
    candidates = scanner.scan()
    daily_log.log_candidates(candidates)
    print(f"\n[scanner] {len(candidates)} candidates passed filters")
    for c in candidates[:10]:
        print(f"  - {c.symbol:<6} score={c.quality_score:.2f}  "
              f"avg_iv={c.avg_iv:.0%}  expirations={len(c.expirations_in_window)}")

    if not candidates:
        daily_log.log_event("no_candidates")
        print("\n>>> No candidates today.")
        print(daily_summary(daily_log, regime, candidates, [], []))
        return 0

    # 3. Build proposals.
    proposals = builder.build_for_candidates(candidates, top_n_per=2)
    for p in proposals:
        daily_log.log_trade({"phase": "built", "proposal": p.to_dict()})
    print(f"\n[builder] {len(proposals)} proposals constructed")

    if not proposals:
        print("\n>>> No proposals survived strike/POP/credit filters.")
        print(daily_summary(daily_log, regime, candidates, proposals, []))
        return 0

    # 4. Validate top-N.
    top = proposals[: args.top]
    validations = []
    if args.no_validate:
        print(f"\n[validator] skipped (--no-validate); rendering top {len(top)}")
    else:
        print(f"\n[validator] running real-time checks on top {len(top)}")
        for p in top:
            v = validator.validate(p)
            validations.append(v)
            daily_log.log_decision("validation", v)

    # 5. Render execution cards.
    print("\n" + "=" * 56)
    print("  EXECUTION-READY TRADE CARDS")
    print("=" * 56)
    for i, p in enumerate(top):
        v = validations[i] if validations else None
        if v is not None and not v.valid:
            print(f"\n[skip] {p.symbol} {p.strategy} INVALID:")
            for r in v.reasons:
                print(f"  - {r}")
            continue
        card = format_trade_card(p, v, contracts=1)
        print()
        print(card)
        daily_log.log_trade({"phase": "rendered", "card": card,
                             "proposal": p.to_dict(),
                             "validation": v.to_dict() if v else None})

    # 6. Daily summary.
    print()
    print(daily_summary(daily_log, regime, candidates, proposals, validations))
    daily_log.log_event("run_finished", counts=daily_log.counts())
    return 0


def run_backtest(args: argparse.Namespace) -> int:
    from .backtester import Backtester  # local import keeps live path lean

    start, end = (_parse_date(args.backtest[0]), _parse_date(args.backtest[1]))
    print(f"[backtest] {start} -> {end}")
    bt = Backtester()
    result = bt.run(start, end)
    metrics = result.metrics()
    print("\n=== Backtest metrics ===")
    for k, v in metrics.items():
        if k == "by_regime":
            print("by_regime:")
            for r, stats in v.items():
                print(f"  {r}: {stats}")
        else:
            print(f"{k}: {v}")
    return 0


def main(argv: List[str] | None = None) -> int:
    args = _argparser().parse_args(argv)
    _setup_logging(args.verbose)
    # Touch every config so missing files surface early.
    for name in ("strategy_rules", "regime_config", "failure_logic",
                 "scanner_config", "data_config"):
        load_config(name)
    if args.backtest:
        return run_backtest(args)
    return run_live(args)


if __name__ == "__main__":
    sys.exit(main())
