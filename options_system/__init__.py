"""Options income system — Phase 1 / 30-day build.

A modular, rules-based premium-selling pipeline:

    regime_engine -> scanner -> trade_builder -> validator -> execution

Each subpackage is independently testable. Configs in `config/` drive all
thresholds. The `data/` package abstracts the market-data source so yfinance
can be swapped for Tradier/Polygon later without touching business logic.
"""

__version__ = "0.1.0"
