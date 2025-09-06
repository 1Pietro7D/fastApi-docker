# app/Controllers/user_roles_controller.py

from fastapi import Depends, HTTPException                      # Import delle utilità FastAPI (DI, eccezioni HTTP)
from sqlalchemy.ext.asyncio import AsyncSession                 # Sessione async SQLAlchemy
from uuid import UUID                                           # Tipo UUID per identificativi
from app.Infrastructure.db import get_db                        # Dependency: restituisce una sessione DB async
from app.Services.role_service import RoleService               # Service per la logica di business sui ruoli e user_roles
from app.Schemas.user_role import AssignRoleInput               # Schema Pydantic per input di assegnazione ruolo
from app.Schemas.role import RoleRead                           # Schema Pydantic di output per i ruoli


class UserRolesController:
    def __init__(self): ...                                     # Nessuna inizializzazione speciale

    async def list_user_roles(
        self,
        user_id: UUID,                                          # Utente per cui elencare i ruoli
        db: AsyncSession = Depends(get_db),                     # Sessione DB async iniettata da FastAPI
    ) -> list[RoleRead]:                                        # Ritorna lista di ruoli (DTO Pydantic)
        svc = RoleService(db)                                   # Istanzia il service ruoli
        roles = await svc.user_roles.list_user_roles(user_id)   # Deve restituire una lista di oggetti Role (join sul ponte)
        return [RoleRead.model_validate(r) for r in roles]      # Serializza in DTO coerenti

    async def assign_role(
        self,
        payload: AssignRoleInput,                               # Body JSON validato (user_id + role_id)
        db: AsyncSession = Depends(get_db),                     # Sessione DB async
    ) -> RoleRead:                                              # Ritorna il ruolo appena assegnato (DTO)
        svc = RoleService(db)                                   # Istanzia il service
        await svc.user_roles.assign(payload.user_id, payload.role_id)  # Crea la riga nella tabella ponte
        role = await svc.roles.get(payload.role_id)             # Rilegge il ruolo per restituirlo in output
        if not role:
            # Caso limite: ponte creato ma ruolo non più disponibile
            raise HTTPException(status_code=404, detail="Ruolo non trovato dopo l'assegnazione")
        return RoleRead.model_validate(role)

    async def unassign_role(
        self,
        user_id: UUID,                                          # Utente target (UUID)
        role_id: UUID,                                          # Ruolo da rimuovere (UUID)
        db: AsyncSession = Depends(get_db),                     # Sessione DB async
    ) -> dict:                                                  # Ritorna conferma di eliminazione
        svc = RoleService(db)                                   # Istanzia il service
        ok = await svc.user_roles.unassign(user_id, role_id)    # Prova a rimuovere l’associazione
        if not ok:                                              # Se non trovata
            raise HTTPException(status_code=404, detail="Assegnazione non trovata")
        return {"deleted": True}                                # Conferma di cancellazione
