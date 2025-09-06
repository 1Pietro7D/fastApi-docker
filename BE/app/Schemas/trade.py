# app/Schemas/trade.py

from __future__ import annotations

from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class TradeCreate(BaseModel):
    symbol: str
    p_l: Optional[float] = None
    setup: Optional[str] = None
    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None
    notes: Optional[str] = None
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    position_size: Optional[float] = None
    lowest_price_during_trade: Optional[float] = None
    highest_price_during_trade: Optional[float] = None
    direction: Optional[str] = None  # enum PostgreSQL "trade_direction"
    emotional_state: Optional[str] = Field(default=None, max_length=50)
    mistakes: Optional[List[str]] = None
    notes_pre_trade: Optional[str] = None
    notes_post_trade: Optional[str] = None
    entry_timestamp: Optional[datetime] = None
    exit_timestamp: Optional[datetime] = None
    tags: Optional[List[str]] = None  # nomi tag da associare


class TradeUpdate(BaseModel):
    symbol: Optional[str] = None
    p_l: Optional[float] = None
    setup: Optional[str] = None
    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None
    notes: Optional[str] = None
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    position_size: Optional[float] = None
    lowest_price_during_trade: Optional[float] = None
    highest_price_during_trade: Optional[float] = None
    direction: Optional[str] = None
    emotional_state: Optional[str] = Field(default=None, max_length=50)
    mistakes: Optional[List[str]] = None
    notes_pre_trade: Optional[str] = None
    notes_post_trade: Optional[str] = None
    entry_timestamp: Optional[datetime] = None
    exit_timestamp: Optional[datetime] = None
    tags: Optional[List[str]] = None  # se presente → sostituisce le associazioni


class TradeRead(BaseModel):
    id: UUID
    created_at: datetime
    user_id: UUID

    p_l: Optional[float] = None
    setup: Optional[str] = None
    stop_loss_price: Optional[float] = None
    take_profit_price: Optional[float] = None
    notes: Optional[str] = None
    entry_price: Optional[float] = None
    exit_price: Optional[float] = None
    position_size: Optional[float] = None
    lowest_price_during_trade: Optional[float] = None
    highest_price_during_trade: Optional[float] = None
    symbol: Optional[str] = None
    direction: Optional[str] = None
    emotional_state: Optional[str] = None
    mistakes: Optional[List[str]] = None
    notes_pre_trade: Optional[str] = None
    notes_post_trade: Optional[str] = None
    entry_timestamp: Optional[datetime] = None
    exit_timestamp: Optional[datetime] = None

    tags: List[str] = []

    class Config:
        from_attributes = True


class TradeFilters(BaseModel):
    symbol: Optional[str] = None
    direction: Optional[str] = None
    setups: Optional[List[str]] = None
    mistakes: Optional[List[str]] = None
    days_of_week: Optional[List[int]] = None  # 1..7 ISO DOW
    min_size: Optional[float] = None
    max_size: Optional[float] = None
    tags: Optional[List[str]] = None
