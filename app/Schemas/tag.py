# app/Schemas/tag.py

from __future__ import annotations

from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    name: str = Field(..., max_length=50)
    color: Optional[str] = Field(default="#888888", max_length=7)


class TagUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=50)
    color: Optional[str] = Field(default=None, max_length=7)


class TagRead(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    color: Optional[str] = None

    class Config:
        from_attributes = True
