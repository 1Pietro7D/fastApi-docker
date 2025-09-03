from sqlalchemy.ext.asyncio import AsyncSession
from app.Repositories.role_repository import RoleRepository
from app.Repositories.user_role_repository import UserRoleRepository

class RoleService:
    def __init__(self, db: AsyncSession):
        self.roles = RoleRepository(db)
        self.user_roles = UserRoleRepository(db)
