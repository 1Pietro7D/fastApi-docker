# app/Controllers/roles_controller.py

from fastapi import Depends, HTTPException                    # Utilità FastAPI: dependency injection, eccezioni HTTP
from sqlalchemy.ext.asyncio import AsyncSession               # Sessione asincrona di SQLAlchemy
from uuid import UUID                                         # Tipo UUID per gli identificativi
from app.Infrastructure.db import get_db                      # Dependency: fornisce una AsyncSession
from app.Services.role_service import RoleService             # Service: logica di business per ruoli e user_roles
from app.Schemas.role import (                                # Schemi Pydantic (input/output) per i ruoli
    RoleCreate,
    RoleUpdate,
    RoleRead,
)
class RolesController:
    def __init__(self): ...                                   # Nessuna init specifica (controller stateless)

    async def list_roles(
        self,
        db: AsyncSession = Depends(get_db),                   # Inietta la sessione DB asincrona
    ) -> list[RoleRead]:                                      # Ritorna una lista di DTO di ruoli
        svc = RoleService(db)                                 # Istanzia il service ruoli
        rows = await svc.roles.list()                         # Chiede al service l’elenco dei ruoli
        return [RoleRead.model_validate(r) for r in rows]     # Serializza/valida con Pydantic per l’output

    async def get_role(
        self,
        role_id: UUID,                                        # ID del ruolo (UUID, allineato al DB)
        db: AsyncSession = Depends(get_db),                   # Sessione DB asincrona
    ) -> RoleRead:                                            # Ritorna il DTO del ruolo
        svc = RoleService(db)                                 # Istanzia il service ruoli
        row = await svc.roles.get(role_id)                    # Recupera il ruolo per ID
        if not row:                                           # Se non trovato
            raise HTTPException(status_code=404,              # Risponde con 404 Not Found
                                detail="Ruolo non trovato")
        return RoleRead.model_validate(row)                   # Serializza il record trovato

    async def create_role(
        self,
        payload: RoleCreate,                                  # Body JSON validato per la creazione
        db: AsyncSession = Depends(get_db),                   # Sessione DB asincrona
    ) -> RoleRead:                                            # Ritorna il DTO del ruolo creato
        svc = RoleService(db)                                 # Istanzia il service ruoli
        row = await svc.roles.create(payload.model_dump())    # Crea il ruolo (passa i campi del payload)
        return RoleRead.model_validate(row)                   # Serializza il risultato

    async def update_role(
        self,
        role_id: UUID,                                        # ID del ruolo da aggiornare
        payload: RoleUpdate,                                  # Body con campi parziali aggiornabili
        db: AsyncSession = Depends(get_db),                   # Sessione DB asincrona
    ) -> RoleRead:                                            # Ritorna il DTO aggiornato
        svc = RoleService(db)                                 # Istanzia il service ruoli
        row = await svc.roles.update(                         # Esegue l’aggiornamento
            role_id,
            payload.model_dump(exclude_none=True)             # Esclude i None → comportamento tipo PATCH
        )
        if not row:                                           # Se il ruolo non esiste
            raise HTTPException(status_code=404,              # 404 Not Found
                                detail="Ruolo non trovato")
        return RoleRead.model_validate(row)                   # Serializza il record aggiornato

    async def delete_role(
        self,
        role_id: UUID,                                        # ID del ruolo da eliminare
        db: AsyncSession = Depends(get_db),                   # Sessione DB asincrona
    ) -> dict:                                                # Ritorna un esito semplice
        svc = RoleService(db)                                 # Istanzia il service ruoli
        ok = await svc.roles.delete(role_id)                  # Prova a eliminare il ruolo
        if not ok:                                            # Se non trovato/già eliminato
            raise HTTPException(status_code=404,              # 404 Not Found
                                detail="Ruolo non trovato")
        return {"deleted": True}                              # Esito standard
