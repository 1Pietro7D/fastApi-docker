from fastapi import Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.Infrastructure.db import get_db
from app.Services.user_service import UserService
from app.Schemas.auth_user import AuthUserCreate, AuthUserUpdate, AuthUserRead
from app.Router.auth import require_roles

class UsersController:
    def __init__(self): ...

    async def list_users(
        self,
        offset: int = 0,
        limit: int = Query(50, le=200),
        db: AsyncSession = Depends(get_db),
        _claims: dict = Depends(require_roles(["admin"]))  # <<<< QUI
    ) -> list[AuthUserRead]:
        svc = UserService(db)
        rows = await svc.list_users(offset, limit)
        return [AuthUserRead.model_validate(r) for r in rows]

    async def get_user(
        self,
        user_id: str,
        db: AsyncSession = Depends(get_db),
        _claims: dict = Depends(require_roles(["admin"]))  # <<<< QUI
    ) -> AuthUserRead:
        svc = UserService(db)
        row = await svc.get_user(user_id)
        if not row:
            raise HTTPException(status_code=404, detail="User non trovato")
        return AuthUserRead.model_validate(row)

    async def create_user(
        self,
        payload: AuthUserCreate,
        db: AsyncSession = Depends(get_db),
        _claims: dict = Depends(require_roles(["admin"]))  # <<<< QUI
    ) -> AuthUserRead:
        svc = UserService(db)
        row = await svc.create_user_via_supabase(payload)
        if not row:
            raise HTTPException(status_code=500, detail="Creato su Supabase ma non trovato nel DB")
        return AuthUserRead.model_validate(row)

    async def update_user(
        self,
        user_id: str,
        payload: AuthUserUpdate,
        db: AsyncSession = Depends(get_db),
        _claims: dict = Depends(require_roles(["admin"]))  # <<<< QUI
    ) -> AuthUserRead:
        svc = UserService(db)
        row = await svc.update_user(user_id, payload.model_dump(exclude_none=True))
        if not row:
            raise HTTPException(status_code=404, detail="User non trovato")
        return AuthUserRead.model_validate(row)

    async def delete_user(
        self,
        user_id: str,
        db: AsyncSession = Depends(get_db),
        _claims: dict = Depends(require_roles(["admin"]))  # <<<< QUI
    ) -> dict:
        svc = UserService(db)
        ok = await svc.delete_user(user_id)
        if not ok:
            raise HTTPException(status_code=404, detail="User non trovato")
        return {"deleted": True}
