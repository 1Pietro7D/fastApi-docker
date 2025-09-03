from pydantic import BaseModel
from uuid import UUID

class AssignRoleInput(BaseModel):
    user_id: UUID
    role_id: int
