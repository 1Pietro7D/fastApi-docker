# app/Repositories/auth_user_repository.py
from __future__ import annotations

from typing import Optional, Sequence
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.auth_user import AuthUser

__all__ = ["AuthUserRepository"]  # <-- espone esplicitamente il simbolo


class AuthUserRepository:
    """
    Repository per interrogare/modificare la tabella `auth.users` (mappata dal modello `AuthUser`).
    NOTA: per campi “sensibili” gestiti da Supabase Auth (es. email/password/phone/ban/meta),
    in produzione è preferibile usare le Admin API (service) e non scrivere direttamente sul DB.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # -------------------------
    # READ
    # -------------------------
    async def get(self, user_id: UUID) -> Optional[AuthUser]:
        """Ritorna un utente per id (UUID) oppure None."""
        return await self.db.get(AuthUser, user_id)

    async def list(self, offset: int = 0, limit: int = 50) -> Sequence[AuthUser]:
        """
        Ritorna un elenco di utenti con paginazione.
        """
        stmt = select(AuthUser).offset(offset).limit(limit)
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def get_by_email(self, email: str) -> Optional[AuthUser]:
        """Ritorna un utente per email (se presente), altrimenti None."""
        stmt = select(AuthUser).where(AuthUser.email == email).limit(1)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    # -------------------------
    # WRITE
    # -------------------------
    async def update(self, user_id: UUID, data: dict) -> Optional[AuthUser]:
        """
        Aggiorna i campi dell'utente con id dato e ritorna la riga aggiornata.
        ATTENZIONE: valuta l'uso del service Supabase Admin per i campi gestiti da Auth.
        """
        if not data:
            # niente da aggiornare
            return await self.get(user_id)

        stmt = (
            update(AuthUser)
            .where(AuthUser.id == user_id)
            .values(**data)
            .returning(AuthUser)
        )
        res = await self.db.execute(stmt)
        row = res.scalar_one_or_none()
        if row:
            await self.db.commit()
        else:
            await self.db.rollback()
        return row

    async def delete(self, user_id: UUID) -> bool:
        """
        Elimina l'utente con id dato.
        Ritorna True se almeno una riga è stata cancellata.
        """
        stmt = delete(AuthUser).where(AuthUser.id == user_id)
        res = await self.db.execute(stmt)
        await self.db.commit()
        return (res.rowcount or 0) > 0
