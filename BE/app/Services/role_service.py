# app/Services/role_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional

from app.Repositories.role_repository import RoleRepository
from app.Repositories.user_role_repository import UserRoleRepository
from app.Models.role import Role
from app.Models.user_role import UserRole

class RoleService:
    """
    Service che orchestra la logica di business relativa ai ruoli e alle
    associazioni utente↔ruolo. Espone:
      - roles:      operazioni CRUD sui ruoli (delegato a RoleRepository)
      - user_roles: operazioni sulla tabella ponte (delegato a UserRoleRepository)
    """

    def __init__(self, db: AsyncSession) -> None:
        self.roles = RoleRepository(db)
        self.user_roles = UserRoleRepository(db)

    # (Facoltativo) Metodi pass-through/addizionali di comodo
    async def list_roles_for_user(self, user_id: UUID) -> List[Role]:
        return await self.user_roles.list_user_roles(user_id)

    async def assign_role_to_user(self, user_id: UUID, role_id: UUID) -> UserRole:
        return await self.user_roles.assign(user_id, role_id)

    async def unassign_role_from_user(self, user_id: UUID, role_id: UUID) -> bool:
        return await self.user_roles.unassign(user_id, role_id)
