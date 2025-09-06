# app/Schemas/user_role.py

from pydantic import BaseModel
from uuid import UUID

# ✅ Schema per l’assegnazione di un ruolo a un utente
# Usato negli endpoint POST /users/assign-role
class AssignRoleInput(BaseModel):
    user_id: UUID   # ID dell’utente (collegato a auth.users.id)
    role_id: UUID   # ID del ruolo (collegato a public.roles.id)


# ✅ Schema per la lettura delle assegnazioni
# Usato negli endpoint GET /users/{user_id}/roles
class UserRoleRead(BaseModel):
    user_id: UUID   # ID utente
    role_id: UUID   # ID ruolo

    class Config:
        from_attributes = True  # consente di creare l’oggetto da un modello SQLAlchemy
