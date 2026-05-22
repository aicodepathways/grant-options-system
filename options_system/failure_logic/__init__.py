"""Configurable risk rules and exit guidance.

Two surfaces:
- `evaluate_proposal`: pre-trade — the trade builder's failure-flag pass.
- `evaluate_open_position`: post-entry — given a live mark and underlying,
  decide whether to hold, scale, or exit.
"""
from .rules import (
    FailureSignal,
    PositionState,
    evaluate_open_position,
    evaluate_proposal,
)

__all__ = [
    "FailureSignal",
    "PositionState",
    "evaluate_proposal",
    "evaluate_open_position",
]
