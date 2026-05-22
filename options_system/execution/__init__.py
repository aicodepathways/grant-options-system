"""Execution outputs.

Phase 1 is manual entry only. This module renders Robinhood-friendly
instructions for a validated TradeProposal: legs, suggested limit price,
and trade-management levels."""
from .formatter import (
    format_trade_card,
    format_trade_card_dict,
    suggested_limit_price,
)

__all__ = ["format_trade_card", "format_trade_card_dict", "suggested_limit_price"]
