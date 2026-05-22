"""Regime classification & deployment gating.

Reads SPX, VIX, and volatility-compression signals; returns a regime label
and a binary DEPLOY / NO-TRADE decision plus a sizing multiplier.
Entirely rules-based for Phase 1 — leaves room for an HMM layer later.
"""
from .engine import RegimeEngine, RegimeReading, classify

__all__ = ["RegimeEngine", "RegimeReading", "classify"]
