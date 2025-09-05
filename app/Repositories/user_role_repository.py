# app/Repositories/user_role_repository.py

from typing import List
from uuid import UUID

from sqlalchemy import select, delete, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

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

    async def user_has_role(self, user_id: UUID, role_name: str) -> bool:
        """
        Verifica se l'utente ha un ruolo con il nome specificato.
        """
        stmt = (
            select(
                exists().where(
                    UserRole.user_id == user_id,
                    UserRole.role_id == Role.id,
                    Role.name == role_name,
                )
            )
            .select_from(UserRole)
            .join(Role, Role.id == UserRole.role_id)
        )
        res = await self.db.execute(stmt)
        return bool(res.scalar())

    async def assign(self, user_id: UUID, role_id: UUID) -> UserRole:
        """
        Crea l'associazione user_id ↔ role_id.
        Esegue commit e ritorna l'oggetto ponte creato.
        """
        row = UserRole(user_id=user_id, role_id=role_id)
        self.db.add(row)
        try:
            await self.db.commit()
        except IntegrityError:
            await self.db.rollback()
            # vincolo UniqueConstraint violato (già assegnato)
            raise
        await self.db.refresh(row)
        return row

    async def unassign(self, user_id: UUID, role_id: UUID) -> bool:
        """
        Elimina l'associazione user_id ↔ role_id.
        Esegue commit. Ritorna True se almeno una riga è stata cancellata.
        """
        stmt = (
            delete(UserRole)
            .where(UserRole.user_id == user_id, UserRole.role_id == role_id)
            .execution_options(synchronize_session="fetch")
        )
        res = await self.db.execute(stmt)
        await self.db.commit()
        return (res.rowcount or 0) > 0
