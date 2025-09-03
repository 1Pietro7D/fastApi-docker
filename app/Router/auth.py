# app/Router/auth.py
from __future__ import annotations

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.Utils.jwt_verify_supabase import verify_supabase_jwt
from app.Infrastructure.db import get_db
from app.Repositories.user_role_repository import UserRoleRepository
from app.config import settings

# auto_error=False: in dev vogliamo poter bypassare anche senza header
bearer = HTTPBearer(auto_error=False)


async def get_current_claims(
    request: Request,
    creds: HTTPAuthorizationCredentials | None = Depends(bearer),
):
    # 🔓 BYPASS in DEV
    if settings.ENV == "dev":
        return {"sub": "DEV-BYPASS"}

    # 🔒 In PROD serve il token
    if creds is None or not creds.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )

    token = creds.credentials
    try:
        claims = verify_supabase_jwt(token)
        return claims
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token non valido"
        )


def require_roles(roles: list[str]):
    async def dep(
        claims=Depends(get_current_claims),
        db: AsyncSession = Depends(get_db),
    ):
        # In dev abbiamo già bypassato: nessun controllo ruoli
        if settings.ENV == "dev":
            return claims

        # In prod: controlla che il token abbia "sub" (user id)
        user_id = claims.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token senza sub")

        # Verifica ruolo nel DB
        repo = UserRoleRepository(db)
        for r in roles:
            if await repo.user_has_role(user_id, r):
                return claims

        raise HTTPException(status_code=403, detail="Ruolo non autorizzato")

    return dep
