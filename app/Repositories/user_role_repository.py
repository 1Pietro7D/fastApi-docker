from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete
from app.Models.user_role import UserRole
from app.Models.role import Role

class UserRoleRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_user_roles(self, user_id: str) -> Sequence[UserRole]:
        res = await self.db.execute(select(UserRole).where(UserRole.user_id == user_id))
        return res.scalars().all()

    async def assign(self, user_id: str, role_id: str) -> UserRole:
        stmt = insert(UserRole).values(user_id=user_id, role_id=role_id).returning(UserRole)
        res = await self.db.execute(stmt)
        row = res.scalar_one()
        await self.db.commit()
        return row

    async def unassign(self, user_id: str, role_id: str) -> bool:
        res = await self.db.execute(
            delete(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
        )
        await self.db.commit()
        return res.rowcount > 0

    async def user_has_role(self, user_id: str, role_name: str) -> bool:
        stmt = (
            select(UserRole)
            .join(Role, Role.id == UserRole.role_id)
            .where(UserRole.user_id == user_id, Role.name == role_name)
        )
        res = await self.db.execute(stmt)
        return res.scalars().first() is not None
