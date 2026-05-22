"""Structured logging.

Three log streams, all JSON-Lines for easy downstream analysis:
- candidates.jsonl   one row per scanner candidate per run
- decisions.jsonl    regime / validation / failure-logic decisions
- trades.jsonl       trade proposals + validation outcomes
Plus a daily summary printed to stdout at end of run.
"""
from .logger import DailyLogger, daily_summary

__all__ = ["DailyLogger", "daily_summary"]
