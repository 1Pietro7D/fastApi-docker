# app/Repositories/auth_user_repository.py
from __future__ import annotations

from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.Models.auth_user import AuthUser

__all__ = ["AuthUserRepository"]  # <-- espone esplicitamente il simbolo


class AuthUserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, user_id: str) -> Optional[AuthUser]:
        return await self.db.get(AuthUser, user_id)

    async def list(self, offset: int = 0, limit: int = 50) -> Sequence[AuthUser]:
        res = await self.db.execute(
            select(AuthUser).offset(offset).limit(limit)
        )
        return res.scalars().all()

    async def update(self, user_id: str, data: dict) -> Optional[AuthUser]:
        stmt = (
            update(AuthUser)
            .where(AuthUser.id == user_id)
            .values(**data)
            .returning(AuthUser)
        )
        res = await self.db.execute(stmt)
        row = res.scalar_one_or_none()
        if row:
            await self.db.commit()
        return row

    async def delete(self, user_id: str) -> bool:
        res = await self.db.execute(
            delete(AuthUser).where(AuthUser.id == user_id)
        )
        await self.db.commit()
        return (res.rowcount or 0) > 0
