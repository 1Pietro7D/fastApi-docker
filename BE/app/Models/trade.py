# app/Models/trade.py
# Modello SQLAlchemy per la tabella public.trades

from __future__ import annotations

import uuid
from typing import Any, Optional, TYPE_CHECKING

from sqlalchemy import (
    String,
    Text,
    TIMESTAMP,
    ForeignKey,
    Index,
    UniqueConstraint,
    Numeric,
    Float,
    func,
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.db import Base

if TYPE_CHECKING:
    # Solo per Pylance / type-checker (evita cicli d'import)
    from app.Models.trades_tags import TradesTags
    from app.Models.tag import Tag


class Trade(Base):
    __tablename__ = "trades"
    __table_args__ = (
        UniqueConstraint("id", "user_id", name="trades_id_user_id_key"),
        Index("idx_trades_user", "user_id"),
        {"schema": "public"},
    )

    # chiavi
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # campi base
    created_at: Mapped[Any] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, server_default=func.now()
    )
    p_l: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # prezzi/size
    setup: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stop_loss_price: Mapped[Optional[Numeric]] = mapped_column(Numeric, nullable=True)
    take_profit_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    entry_price: Mapped[Optional[Numeric]] = mapped_column(Numeric, nullable=True)
    exit_price: Mapped[Optional[Numeric]] = mapped_column(Numeric, nullable=True)
    position_size: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    lowest_price_during_trade: Mapped[Optional[Numeric]] = mapped_column(
        Numeric, nullable=True
    )
    highest_price_during_trade: Mapped[Optional[Numeric]] = mapped_column(
        Numeric, nullable=True
    )

    # extra
    symbol: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    direction: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )  # in DB è enum
    emotional_state: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    mistakes: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text), nullable=True)
    notes_pre_trade: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes_post_trade: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    entry_timestamp: Mapped[Optional[Any]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )
    exit_timestamp: Mapped[Optional[Any]] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

    # relazioni (scrittura tramite tabella ponte)
    tag_links: Mapped[list["TradesTags"]] = relationship(
        "TradesTags",
        back_populates="trade",
        cascade="all, delete-orphan",
        passive_deletes=True,
        overlaps="trade_links,tag",
    )

    # relazione many-to-many di sola lettura verso Tag
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary="public.trades_tags",
        primaryjoin="Trade.id==TradesTags.trade_id",
        secondaryjoin="Tag.id==TradesTags.tag_id",
        viewonly=True,
        overlaps="trade_links,tag_links",
    )
