"""Daily JSON-Lines logger."""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from ..config import logs_dir

logger = logging.getLogger(__name__)


def _to_jsonable(obj: Any) -> Any:
    if obj is None or isinstance(obj, (bool, int, float, str)):
        return obj
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if is_dataclass(obj):
        return {k: _to_jsonable(v) for k, v in asdict(obj).items()}
    if isinstance(obj, dict):
        return {str(k): _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, set)):
        return [_to_jsonable(v) for v in obj]
    return repr(obj)


class DailyLogger:
    """Append-only JSONL writer with one file-per-day-per-stream.

    Streams are flushed after each write so a crash mid-run doesn't lose
    candidate/decision data.
    """

    STREAMS = ("candidates", "decisions", "trades", "events")

    def __init__(self, run_date: Optional[date] = None) -> None:
        self.run_date = run_date or date.today()
        self.dir = logs_dir() / self.run_date.isoformat()
        self.dir.mkdir(parents=True, exist_ok=True)
        self._counts: Dict[str, int] = {s: 0 for s in self.STREAMS}

    def _path(self, stream: str) -> Path:
        if stream not in self.STREAMS:
            raise ValueError(f"unknown stream {stream}")
        return self.dir / f"{stream}.jsonl"

    def log(self, stream: str, payload: Any) -> None:
        record = {
            "ts": datetime.utcnow().isoformat(),
            "stream": stream,
            "data": _to_jsonable(payload),
        }
        with self._path(stream).open("a") as f:
            f.write(json.dumps(record, default=str) + "\n")
        self._counts[stream] = self._counts.get(stream, 0) + 1

    # convenience methods --------------------------------------------------

    def log_candidates(self, candidates: Iterable[Any]) -> None:
        for c in candidates:
            self.log("candidates", c)

    def log_decision(self, kind: str, payload: Any) -> None:
        self.log("decisions", {"kind": kind, "payload": _to_jsonable(payload)})

    def log_trade(self, payload: Any) -> None:
        self.log("trades", payload)

    def log_event(self, message: str, **kwargs: Any) -> None:
        self.log("events", {"message": message, **kwargs})

    def counts(self) -> Dict[str, int]:
        return dict(self._counts)


def daily_summary(
    logger_obj: DailyLogger,
    regime: Optional[Any],
    candidates: List[Any],
    proposals: List[Any],
    validations: List[Any],
) -> str:
    """Return a one-screen daily summary string."""
    lines: List[str] = []
    lines.append(f"=== Daily Summary  {logger_obj.run_date.isoformat()} ===")
    if regime is not None:
        rd = regime.to_dict() if hasattr(regime, "to_dict") else regime
        lines.append(f"Regime: {rd.get('regime')}  deploy={rd.get('deploy')}  "
                     f"size_mult={rd.get('size_mult')}")
        for r in rd.get("reasons", []):
            lines.append(f"  - {r}")
    lines.append(f"Candidates: {len(candidates)}")
    lines.append(f"Proposals built: {len(proposals)}")
    valid = [v for v in validations if getattr(v, "valid", False)]
    invalid = [v for v in validations if not getattr(v, "valid", True)]
    lines.append(f"Validated VALID:   {len(valid)}")
    lines.append(f"Validated INVALID: {len(invalid)}")
    if valid:
        lines.append("Top valid trades:")
        for v in valid[:5]:
            p = v.proposal
            lines.append(
                f"  {p.symbol} {p.strategy} exp {p.expiration} "
                f"credit ${p.credit:.2f}  POP {p.pop:.0%}  rank {p.rank_score:.2f}"
            )
    lines.append(f"Logs at: {logger_obj.dir}")
    return "\n".join(lines)
