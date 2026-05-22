"""Trade proposal data models."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Optional


@dataclass
class TradeLeg:
    action: str          # 'SELL' or 'BUY'
    right: str           # 'C' or 'P'
    strike: float
    expiration: date
    quantity: int = 1
    mid: float = 0.0
    bid: float = 0.0
    ask: float = 0.0
    delta: Optional[float] = None
    iv: Optional[float] = None
    contract_symbol: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "right": self.right,
            "strike": self.strike,
            "expiration": self.expiration.isoformat(),
            "quantity": self.quantity,
            "mid": self.mid,
            "bid": self.bid,
            "ask": self.ask,
            "delta": self.delta,
            "iv": self.iv,
            "contract_symbol": self.contract_symbol,
        }


@dataclass
class TradeProposal:
    symbol: str
    strategy: str                  # 'BULL_PUT', 'BEAR_CALL', 'IRON_CONDOR'
    expiration: date
    underlying_price: float
    legs: List[TradeLeg]
    credit: float                  # net credit per spread (per share basis)
    width: float                   # widest defined-risk width
    max_loss: float                # width - credit
    pop: float                     # estimated probability of profit
    # "Early-red flip": the underlying level at which, days_forward days from
    # now, the M2M loss exceeds early_red_loss_pct of credit. This is the
    # path-aware risk threshold — what the client cares about for live risk.
    m2m_flip_price: float
    m2m_flip_distance_pct: float
    # Expiration breakeven: short_strike ± credit. Kept alongside because some
    # traders / failure rules still reason about it.
    expiration_breakeven_price: float
    expiration_breakeven_distance_pct: float
    expected_move: float           # 1 std dev expected move to expiration
    atr: float
    early_red_pl_score: float      # 0..1, lower = goes red faster under stress
    exit_50pct_target_credit: float
    exit_25pct_target_credit: float
    est_days_to_50pct: int
    est_days_to_25pct: int
    rank_score: float = 0.0
    rank_reasons: List[str] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

    @property
    def credit_to_width_ratio(self) -> float:
        return self.credit / self.width if self.width > 0 else 0.0

    @property
    def short_strike(self) -> float:
        sells = [l for l in self.legs if l.action == "SELL"]
        if not sells:
            return float("nan")
        if self.strategy == "BULL_PUT":
            return max(l.strike for l in sells)
        if self.strategy == "BEAR_CALL":
            return min(l.strike for l in sells)
        return sells[0].strike

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "strategy": self.strategy,
            "expiration": self.expiration.isoformat(),
            "underlying_price": self.underlying_price,
            "legs": [l.to_dict() for l in self.legs],
            "credit": self.credit,
            "width": self.width,
            "max_loss": self.max_loss,
            "credit_to_width_ratio": self.credit_to_width_ratio,
            "pop": self.pop,
            "m2m_flip_price": self.m2m_flip_price,
            "m2m_flip_distance_pct": self.m2m_flip_distance_pct,
            "expiration_breakeven_price": self.expiration_breakeven_price,
            "expiration_breakeven_distance_pct": self.expiration_breakeven_distance_pct,
            "expected_move": self.expected_move,
            "atr": self.atr,
            "early_red_pl_score": self.early_red_pl_score,
            "exit_50pct_target_credit": self.exit_50pct_target_credit,
            "exit_25pct_target_credit": self.exit_25pct_target_credit,
            "est_days_to_50pct": self.est_days_to_50pct,
            "est_days_to_25pct": self.est_days_to_25pct,
            "rank_score": self.rank_score,
            "rank_reasons": list(self.rank_reasons),
            "flags": list(self.flags),
            "metrics": dict(self.metrics),
        }
