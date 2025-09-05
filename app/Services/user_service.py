# app/Services/user_service.py

from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.Repositories.auth_user_repository import AuthUserRepository
from app.Infrastructure import supabase_service
from app.Schemas.auth_user import AuthUserCreate
from app.Models.auth_user import AuthUser


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = AuthUserRepository(db)

    async def create_user_via_supabase(self, payload: AuthUserCreate) -> Optional[AuthUser]:
        res = await supabase_service.register_user(
            email=payload.email,
            password=payload.password,
            user_meta=payload.user_meta,
            app_meta=payload.app_meta,
            banned_until=payload.banned_until,
            phone=payload.phone,
        )
        if res.get("error"):
            # qui lasciamo ValueError: il controller lo trasforma in 500; valuta gestione 4xx/5xx a livello controller
            raise ValueError(f"Supabase register error: {res.get('message')}")

        user_id = (res.get("user") or {}).get("id")
        if not user_id:
            raise ValueError("Supabase response senza user.id")

        # ricarica la row da auth.users (UUID coerente col modello/repo)
        user_uuid = UUID(user_id)
        row = await self.repo.get(user_uuid)
        return row

    async def list_users(self, offset=0, limit=50):
        return await self.repo.list(offset, limit)

    async def get_user(self, user_id: UUID):
        return await self.repo.get(user_id)

    async def update_user(self, user_id: UUID, data: dict):
        return await self.repo.update(user_id, data)

    async def delete_user(self, user_id: UUID) -> bool:
        return await self.repo.delete(user_id)
