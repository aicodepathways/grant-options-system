"""Candidate generation. Screens the configured universe for names whose
chains pass IV / liquidity / compression filters."""
from .scanner import Scanner, Candidate

__all__ = ["Scanner", "Candidate"]
