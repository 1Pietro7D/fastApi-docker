from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.Infrastructure.db import get_db
from app.Services.role_service import RoleService
from app.Schemas.user_role import AssignRoleInput
from app.Router.auth import require_roles

class UserRolesController:
    def __init__(self): ...

    async def list_user_roles(self, user_id: str, db: AsyncSession = Depends(get_db)) -> list[dict]:
        await require_roles(["admin"])()
        svc = RoleService(db)
        rows = await svc.user_roles.list_user_roles(user_id)
        return rows

    async def assign_role(self, payload: AssignRoleInput, db: AsyncSession = Depends(get_db)) -> dict:
        await require_roles(["admin"])()
        svc = RoleService(db)
        row = await svc.user_roles.assign(str(payload.user_id), payload.role_id)
        return row

    async def unassign_role(self, user_id: str, role_id: int, db: AsyncSession = Depends(get_db)) -> dict:
        await require_roles(["admin"])()
        svc = RoleService(db)
        ok = await svc.user_roles.unassign(user_id, role_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Assegnazione non trovata")
        return {"deleted": True}
