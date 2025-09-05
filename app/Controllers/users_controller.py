# app/Controllers/users_controller.py

from fastapi import Depends, HTTPException, Query               # Import delle utilità FastAPI (DI, errori, query)
from sqlalchemy.ext.asyncio import AsyncSession                 # Sessione async SQLAlchemy
from app.Infrastructure.db import get_db                        # Dependency per ottenere la sessione DB
from app.Services.user_service import UserService               # Service che incapsula la business logic sugli utenti
from app.Schemas.auth_user import (                             # Schemi Pydantic: input/output
    AuthUserCreate,
    AuthUserUpdate,
    AuthUserRead,
)
from uuid import UUID                                           # Tipi UUID per gli identificativi

class UsersController:
    def __init__(self): ...                                     # Nessuna inizializzazione particolare

    async def list_users(
        self,
        offset: int = 0,                                        # Paginazione: da quale record partire (default 0)
        limit: int = Query(50, le=200),                         # Paginazione: quanti record (max 200)
        db: AsyncSession = Depends(get_db),                     # Sessione DB async iniettata da FastAPI
    ) -> list[AuthUserRead]:                                    # Ritorna una lista serializzabile di utenti
        svc = UserService(db)                                   # Istanzia il service passandogli la sessione
        rows = await svc.list_users(offset, limit)              # Recupera gli utenti dal repository via service
        return [AuthUserRead.model_validate(r) for r in rows]   # Valida/serializza con Pydantic (DTO di output)

    async def get_user(
        self,
        user_id: UUID,                                          # ID utente come UUID (allineato al DB)
        db: AsyncSession = Depends(get_db),                     # Sessione DB async iniettata
    ) -> AuthUserRead:                                          # Ritorna il DTO utente
        svc = UserService(db)                                   # Istanzia il service
        row = await svc.get_user(user_id)                       # Recupera il singolo utente
        if not row:                                             # Se non trovato
            raise HTTPException(status_code=404, detail="User non trovato")  # 404 Not Found
        return AuthUserRead.model_validate(row)                 # Serializza il record a schema di lettura

    async def create_user(
        self,
        payload: AuthUserCreate,                                # Body JSON validato (email/password/meta)
        db: AsyncSession = Depends(get_db),                     # Sessione DB async
    ) -> AuthUserRead:                                          # Ritorna il DTO del nuovo utente
        svc = UserService(db)                                   # Istanzia il service
        row = await svc.create_user_via_supabase(payload)       # Crea l’utente tramite Supabase Admin API
        if not row:                                             # Se non riesce a rileggere dal DB
            raise HTTPException(                                # Errore applicativo coerente
                status_code=500,
                detail="Creato su Supabase ma non trovato nel DB"
            )
        return AuthUserRead.model_validate(row)                 # Serializza il risultato

    async def update_user(
        self,
        user_id: UUID,                                          # Utente da aggiornare (UUID)
        payload: AuthUserUpdate,                                # Body parziale con i campi aggiornabili
        db: AsyncSession = Depends(get_db),                     # Sessione DB async
    ) -> AuthUserRead:                                          # Ritorna il DTO aggiornato
        svc = UserService(db)                                   # Istanzia il service
        row = await svc.update_user(                            # Esegue update con i soli campi presenti
            user_id,
            payload.model_dump(exclude_none=True)               # Rimuove i None per PATCH-like behavior
        )
        if not row:                                             # Se l’utente non esiste
            raise HTTPException(status_code=404, detail="User non trovato")  # 404 Not Found
        return AuthUserRead.model_validate(row)                 # Serializza l’utente aggiornato

    async def delete_user(
        self,
        user_id: UUID,                                          # Utente da eliminare (UUID)
        db: AsyncSession = Depends(get_db),                     # Sessione DB async
    ) -> dict:                                                  # Ritorna un semplice esito JSON
        svc = UserService(db)                                   # Istanzia il service
        ok = await svc.delete_user(user_id)                     # Esegue la cancellazione
        if not ok:                                              # Se non esiste/già cancellato
            raise HTTPException(status_code=404, detail="User non trovato")  # 404 Not Found
        return {"deleted": True}                                # Esito standard
