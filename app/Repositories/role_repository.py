# app/Repositories/role_repository.py
from typing import Sequence, Optional
from uuid import UUID

from sqlalchemy import select, update, delete, insert
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
    # WRITE
    # -------------------------
    async def create(self, data: dict) -> Role:
        """
        Crea un nuovo ruolo con i dati forniti e ritorna il record appena creato.
        """
        stmt = insert(Role).values(**data).returning(Role)
        res = await self.db.execute(stmt)
        row = res.scalar_one()
        await self.db.commit()
        return row

    async def update(self, role_id: UUID, data: dict) -> Optional[Role]:
        """
        Aggiorna i campi del ruolo specificato.
        Ritorna il ruolo aggiornato, oppure None se non trovato.
        """
        if not data:
            return await self.get(role_id)

        stmt = (
            update(Role)
            .where(Role.id == role_id)
            .values(**data)
            .returning(Role)
        )
        res = await self.db.execute(stmt)
        row = res.scalar_one_or_none()
        if row:
            await self.db.commit()
        else:
            await self.db.rollback()
        return row

    async def delete(self, role_id: UUID) -> bool:
        """
        Elimina il ruolo con id dato.
        Ritorna True se almeno una riga è stata cancellata.
        """
        stmt = delete(Role).where(Role.id == role_id)
        res = await self.db.execute(stmt)
        await self.db.commit()
        return (res.rowcount or 0) > 0
