# app/Models/tag.py
# Modello SQLAlchemy per la tabella public.tags

from __future__ import annotations

import uuid
from typing import Optional, TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Infrastructure.db import Base

if TYPE_CHECKING:
    from app.Models.trades_tags import TradesTags
    from app.Models.trade import Trade


class Tag(Base):
    __tablename__ = "tags"
    __table_args__ = (
        UniqueConstraint("id", "user_id", name="tags_id_user_id_key"),
        UniqueConstraint("user_id", "name", name="tags_user_id_name_key"),
        Index("idx_tags_user", "user_id"),
        {"schema": "public"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("auth.users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True, default="#888888")

    # collegamenti alla tabella ponte
    trade_links: Mapped[list["TradesTags"]] = relationship(
        "TradesTags",
        back_populates="tag",
        cascade="all, delete-orphan",
        passive_deletes=True,
        overlaps="tag_links,trade",
    )

    # relazione many-to-many (viewonly) verso Trade
    trades: Mapped[list["Trade"]] = relationship(
        "Trade",
        secondary="public.trades_tags",
        primaryjoin="Tag.id==TradesTags.tag_id",
        secondaryjoin="Trade.id==TradesTags.trade_id",
        viewonly=True,
        overlaps="trade_links,tag_links",
    )
