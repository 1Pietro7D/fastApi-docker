# app/Models/trades_tags.py
# Modello SQLAlchemy per la tabella ponte public.trades_tags

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.db import Base

if TYPE_CHECKING:
    from app.Models.trade import Trade
    from app.Models.tag import Tag


class TradesTags(Base):
    __tablename__ = "trades_tags"
    __table_args__ = (
        PrimaryKeyConstraint("trade_id", "tag_id", name="trades_tags_pkey"),
        ForeignKeyConstraint(
            ["trade_id", "user_id"],
            ["public.trades.id", "public.trades.user_id"],
            ondelete="CASCADE",
            name="trades_tags_trade_fk",
        ),
        ForeignKeyConstraint(
            ["tag_id", "user_id"],
            ["public.tags.id", "public.tags.user_id"],
            ondelete="CASCADE",
            name="trades_tags_tag_fk",
        ),
        Index("idx_trades_tags_user", "user_id"),
        Index("idx_trades_tags_tag", "tag_id"),
        Index("idx_trades_tags_trade", "trade_id"),
        {"schema": "public"},
    )

    trade_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    tag_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)

    trade: Mapped["Trade"] = relationship(
        "Trade",
        back_populates="tag_links",
        overlaps="trade_links",
    )
    tag: Mapped["Tag"] = relationship(
        "Tag",
        back_populates="trade_links",
        overlaps="trade_links,trade",
    )
