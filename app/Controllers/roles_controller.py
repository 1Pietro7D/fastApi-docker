from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.Infrastructure.db import get_db
from app.Services.role_service import RoleService
from app.Schemas.role import RoleCreate, RoleUpdate, RoleRead
from app.Router.auth import require_roles

class RolesController:
    def __init__(self): ...

    async def list_roles(self, db: AsyncSession = Depends(get_db)) -> list[RoleRead]:
        await require_roles(["admin"])()
        svc = RoleService(db)
        rows = await svc.roles.list()
        return [RoleRead.model_validate(r) for r in rows]

    async def get_role(self, role_id: int, db: AsyncSession = Depends(get_db)) -> RoleRead:
        await require_roles(["admin"])()
        svc = RoleService(db)
        row = await svc.roles.get(role_id)
        if not row:
            raise HTTPException(status_code=404, detail="Ruolo non trovato")
        return RoleRead.model_validate(row)

    async def create_role(self, payload: RoleCreate, db: AsyncSession = Depends(get_db)) -> RoleRead:
        await require_roles(["admin"])()
        svc = RoleService(db)
        row = await svc.roles.create(payload.model_dump())
        return RoleRead.model_validate(row)

    async def update_role(self, role_id: int, payload: RoleUpdate, db: AsyncSession = Depends(get_db)) -> RoleRead:
        await require_roles(["admin"])()
        svc = RoleService(db)
        row = await svc.roles.update(role_id, payload.model_dump(exclude_none=True))
        if not row:
            raise HTTPException(status_code=404, detail="Ruolo non trovato")
        return RoleRead.model_validate(row)

    async def delete_role(self, role_id: int, db: AsyncSession = Depends(get_db)) -> dict:
        await require_roles(["admin"])()
        svc = RoleService(db)
        ok = await svc.roles.delete(role_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Ruolo non trovato")
        return {"deleted": True}
