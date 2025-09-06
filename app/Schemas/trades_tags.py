# app/Schemas/trades_tags.py

from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel


class TradesTagsCreate(BaseModel):
    trade_id: UUID
    tag_id: UUID


class TradesTagsDelete(BaseModel):
    trade_id: UUID
    tag_id: UUID


class TradesTagsRead(BaseModel):
    trade_id: UUID
    tag_id: UUID
    user_id: UUID

    class Config:
        from_attributes = True
