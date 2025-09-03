from typing import Sequence, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, insert
from app.Models.role import Role

class RoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list(self, offset=0, limit=100) -> Sequence[Role]:
        res = await self.db.execute(select(Role).offset(offset).limit(limit))
        return res.scalars().all()

    async def get(self, role_id: int) -> Optional[Role]:
        return await self.db.get(Role, role_id)

    async def create(self, data: dict) -> Role:
        stmt = insert(Role).values(**data).returning(Role)
        res = await self.db.execute(stmt)
        row = res.scalar_one()
        await self.db.commit()
        return row

    async def update(self, role_id: int, data: dict) -> Optional[Role]:
        stmt = update(Role).where(Role.id == role_id).values(**data).returning(Role)
        res = await self.db.execute(stmt)
        row = res.scalar_one_or_none()
        if row:
            await self.db.commit()
        return row

    async def delete(self, role_id: int) -> bool:
        res = await self.db.execute(delete(Role).where(Role.id == role_id))
        await self.db.commit()
        return res.rowcount > 0
