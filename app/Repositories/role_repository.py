# app/Repositories/role_repository.py

from typing import Sequence, Optional
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.role import Role


class RoleRepository:
    """
    Repository per la tabella `public.roles`.
    Espone metodi CRUD asincroni per gestire i ruoli dell'applicazione.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # -------------------------
    # READ
    # -------------------------
    async def list(self, offset: int = 0, limit: int = 100) -> Sequence[Role]:
        """
        Ritorna un elenco di ruoli con paginazione.
        """
        stmt = select(Role).offset(offset).limit(limit)
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def get(self, role_id: UUID) -> Optional[Role]:
        """
        Ritorna un ruolo per id, oppure None se non trovato.
        """
        return await self.db.get(Role, role_id)

    # -------------------------
    # WRITE (pattern ORM robusto)
    # -------------------------
    async def create(self, data: dict) -> Role:
        """
        Crea un nuovo ruolo con i dati forniti e ritorna il record appena creato.
        """
        obj = Role(**data)
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def update(self, role_id: UUID, data: dict) -> Optional[Role]:
        """
        Aggiorna i campi del ruolo specificato.
        Ritorna il ruolo aggiornato, oppure None se non trovato.
        """
        obj = await self.db.get(Role, role_id)
        if not obj:
            return None
        if data:
            for k, v in data.items():
                setattr(obj, k, v)
            await self.db.commit()
            await self.db.refresh(obj)
        return obj

    async def delete(self, role_id: UUID) -> bool:
        """
        Elimina il ruolo con id dato.
        Ritorna True se almeno una riga è stata cancellata.
        """
        stmt = delete(Role).where(Role.id == role_id)
        res = await self.db.execute(stmt)
        await self.db.commit()
        return (res.rowcount or 0) > 0
