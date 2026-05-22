"""Adapter factory. Pick a provider via data_config.yaml or env override."""
from __future__ import annotations

import os
from functools import lru_cache

from ..config import load_config
from .base import MarketDataAdapter


@lru_cache(maxsize=None)
def get_adapter(provider: str | None = None) -> MarketDataAdapter:
    """Return a singleton adapter instance for the configured provider.

    Override priority: explicit arg > OPTIONS_DATA_PROVIDER env var > config.
    """
    if provider is None:
        provider = os.environ.get("OPTIONS_DATA_PROVIDER")
    if provider is None:
        provider = load_config("data_config").get("provider", "yfinance")
    provider = provider.lower()

    if provider == "yfinance":
        from .yfinance_adapter import YFinanceAdapter
        return YFinanceAdapter()

    raise ValueError(
        f"Unknown data provider '{provider}'. "
        "Implement MarketDataAdapter and register here."
    )
