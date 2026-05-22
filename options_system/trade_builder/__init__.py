"""Trade construction. Turns a Candidate into one or more concrete trade
proposals (vertical credit spreads, iron condors) with strikes, credit,
POP, M2M flip distance, exit ladders, and a ranking score."""
from .builder import TradeBuilder
from .trade import TradeProposal, TradeLeg

__all__ = ["TradeBuilder", "TradeProposal", "TradeLeg"]
