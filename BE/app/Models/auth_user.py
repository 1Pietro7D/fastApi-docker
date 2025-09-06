# app/Models/auth_user.py

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import String, Boolean, SmallInteger, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.Infrastructure.db import Base


class AuthUser(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "auth"}

    instance_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    aud: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str | None] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255))
    encrypted_password: Mapped[str | None] = mapped_column(String(255))
    email_confirmed_at: Mapped[Any | None] = mapped_column(TIMESTAMP(timezone=True))
    invited_at: Mapped[Any | None] = mapped_column(TIMESTAMP(timezone=True))
    confirmation_token: Mapped[str | None] = mapped_column(String(255))
    confirmation_sent_at: Mapped[Any | None] = mapped_column(TIMESTAMP(timezone=True))
    recovery_token: Mapped[str | None] = mapped_column(String(255))
    recovery_sent_at: Mapped[Any | None] = mapped_column(TIMESTAMP(timezone=True))
    email_change_token_new: Mapped[str | None] = mapped_column(String(255))
    email_change: Mapped[str | None] = mapped_column(String(255))
    email_change_sent_at: Mapped[Any | None] = mapped_column(TIMESTAMP(timezone=True))
    last_sign_in_at: Mapped[Any | None] = mapped_column(TIMESTAMP(timezone=True))
    raw_app_meta_data: Mapped[dict | None] = mapped_column(JSONB)
    raw_user_meta_data: Mapped[dict | None] = mapped_column(JSONB)
    is_super_admin: Mapped[bool | None] = mapped_column(Boolean)
    created_at: Mapped[Any | None] = mapped_column(TIMESTAMP(timezone=True))
    updated_at: Mapped[Any | None] = mapped_column(TIMESTAMP(timezone=True))
    phone: Mapped[str | None] = mapped_column(Text)
    phone_confirmed_at: Mapped[Any | None] = mapped_column(TIMESTAMP(timezone=True))
    phone_change: Mapped[str | None] = mapped_column(Text, default="")
    phone_change_token: Mapped[str | None] = mapped_column(String(255), default="")
    phone_change_sent_at: Mapped[Any | None] = mapped_column(TIMESTAMP(timezone=True))
    email_change_token_current: Mapped[str | None] = mapped_column(String(255), default="")
    email_change_confirm_status: Mapped[int | None] = mapped_column(SmallInteger, default=0)
    banned_until: Mapped[Any | None] = mapped_column(TIMESTAMP(timezone=True))
    reauthentication_token: Mapped[str | None] = mapped_column(String(255), default="")
    reauthentication_sent_at: Mapped[Any | None] = mapped_column(TIMESTAMP(timezone=True))
    is_sso_user: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted_at: Mapped[Any | None] = mapped_column(TIMESTAMP(timezone=True))
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False)
