# app/Repositories/user_role_repository.py

from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.Models.role import Role
from app.Models.user_role import UserRole

class UserRoleRepository:
    """Repository per la tabella ponte user_roles e query correlate ai ruoli utente."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_user_roles(self, user_id: UUID) -> List[Role]:
        """
        Ritorna direttamente i RUOLI assegnati a user_id, tramite JOIN sul ponte.
        """
        stmt = (
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
        )
        res = await self.db.execute(stmt)
        return res.scalars().all()

    async def assign(self, user_id: UUID, role_id: UUID) -> UserRole:
        """
        Crea l'associazione user_id ↔ role_id.
        Ritorna l'oggetto ponte creato.
        """
        row = UserRole(user_id=user_id, role_id=role_id)
        self.db.add(row)
        # flush per ottenere eventuali default/server-side e rendere disponibile row
        await self.db.flush()
        # refresh per popolare i campi dal DB (se necessario)
        await self.db.refresh(row)
        return row

    async def unassign(self, user_id: UUID, role_id: UUID) -> bool:
        """
        Elimina l'associazione user_id ↔ role_id.
        Ritorna True se almeno una riga è stata cancellata.
        """
        stmt = (
            delete(UserRole)
            .where(UserRole.user_id == user_id, UserRole.role_id == role_id)
            .execution_options(synchronize_session="fetch")
        )
        res = await self.db.execute(stmt)
        # NB: in SQLAlchemy 2.x, rowcount è deprecato in alcuni dialetti; con asyncpg funziona.
        deleted = res.rowcount or 0
        return deleted > 0
