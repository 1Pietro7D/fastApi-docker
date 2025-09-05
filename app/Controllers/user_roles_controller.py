# app/Controllers/user_roles_controller.py

from fastapi import Depends, HTTPException                     # Import delle utilità FastAPI (DI, eccezioni HTTP)
from sqlalchemy.ext.asyncio import AsyncSession                # Sessione async SQLAlchemy
from uuid import UUID                                          # Tipo UUID per identificativi
from app.Infrastructure.db import get_db                       # Dependency: restituisce una sessione DB async
from app.Services.role_service import RoleService              # Service per la logica di business sui ruoli e user_roles
from app.Schemas.user_role import AssignRoleInput              # Schema Pydantic per input di assegnazione ruolo


class UserRolesController:
    def __init__(self): ...                                    # Nessuna inizializzazione speciale

    async def list_user_roles(
        self,
        user_id: UUID,                                         # Utente per cui elencare i ruoli
        db: AsyncSession = Depends(get_db),                    # Sessione DB async iniettata da FastAPI
    ) -> list[dict]:                                           # Ritorna lista di mapping (ruoli assegnati)
        svc = RoleService(db)                                  # Istanzia il service ruoli
        rows = await svc.user_roles.list_user_roles(user_id)   # Chiede al service di recuperare i ruoli per utente
        return rows                                            # Restituisce lista (dizionari o DTO dal service)

    async def assign_role(
        self,
        payload: AssignRoleInput,                              # Body JSON validato (user_id + role_id)
        db: AsyncSession = Depends(get_db),                    # Sessione DB async
    ) -> dict:                                                 # Ritorna il risultato dell’assegnazione
        svc = RoleService(db)                                  # Istanzia il service
        row = await svc.user_roles.assign(                     # Richiama il metodo assign sul ponte user_roles
            str(payload.user_id),                              # Converte UUID in stringa se necessario
            payload.role_id,
        )
        return row                                             # Restituisce il record creato (o simile)

    async def unassign_role(
        self,
        user_id: UUID,                                         # Utente target (UUID)
        role_id: UUID,                                         # Ruolo da rimuovere (UUID)
        db: AsyncSession = Depends(get_db),                    # Sessione DB async
    ) -> dict:                                                 # Ritorna conferma di eliminazione
        svc = RoleService(db)                                  # Istanzia il service
        ok = await svc.user_roles.unassign(user_id, role_id)   # Prova a rimuovere l’associazione
        if not ok:                                             # Se non trovata
            raise HTTPException(                               # Ritorna 404
                status_code=404,
                detail="Assegnazione non trovata"
            )
        return {"deleted": True}                               # Conferma di cancellazione
