# app/Controllers/auth_controller.py

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.Infrastructure.db import get_db
from app.Infrastructure import supabase_service
from app.Router.auth import get_current_claims
from app.Schemas.auth_session import (
    LoginInput,
    LoginResponse,
    RegisterInput,
    RegisterResponse,
    LogoutResponse,
)
from app.config import settings


class AuthController:
    """
    Controller per autenticazione basata su Supabase (GoTrue).
    ✅ Versione "service-key only": TUTTE le chiamate a Supabase usano la SERVICE KEY
       (compreso il password grant per il login).
    Nota: i JWT di accesso sono stateless; il logout revoca solo le sessioni/refresh future.
    """

    def __init__(self) -> None:
        ...

    async def login(
        self,
        payload: LoginInput,                          # email e password
        db: AsyncSession = Depends(get_db),           # sessione DB (non usata direttamente)
    ) -> LoginResponse:
        """
        LOGIN:
        - Chiede a Supabase un access_token/refresh_token via password grant.
        - In questa versione usiamo SEMPRE la SERVICE KEY (non l'anon key).
        """
        res = await supabase_service.sign_in(payload.email, payload.password)
        if res.get("error"):
            # Supabase spesso restituisce un messaggio generico per security;
            # in DEV arricchiamo per debug.
            msg = res.get("message") or "Credenziali non valide"
            if settings.ENV == "dev":
                bits: list[str] = []
                if "http_status" in res:
                    bits.append(f"http_status={res['http_status']}")
                if "error_code" in res:
                    bits.append(f"error_code={res['error_code']}")
                if "raw" in res and isinstance(res["raw"], dict):
                    raw_msg = res["raw"].get("message") or res["raw"].get("error_description")
                    if raw_msg and raw_msg != msg:
                        bits.append(f"raw='{raw_msg}'")
                if bits:
                    msg = f"{msg} ({', '.join(bits)})"
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=msg)

        return LoginResponse(
            access_token=res.get("access_token"),
            token_type=res.get("token_type") or "bearer",
            expires_in=res.get("expires_in"),
            refresh_token=res.get("refresh_token"),
            user=res.get("user") or {},
        )

    async def register(
        self,
        payload: RegisterInput,                       # dati di registrazione
        db: AsyncSession = Depends(get_db),
    ) -> RegisterResponse:
        """
        REGISTRAZIONE:
        - Crea utente con email/password.
        - Applica patch opzionali (app_meta, phone, ecc.) via Admin API.
        - In DEV, se configurato, conferma l'email automaticamente.
        """
        res = await supabase_service.register_user(
            email=payload.email,
            password=payload.password,
            user_meta=payload.user_meta,
            app_meta=payload.app_meta,
            banned_until=None,
            phone=payload.phone,
        )
        if res.get("error"):
            msg = res.get("message") or "Registrazione fallita"
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)

        user = (res.get("user") or {})
        return RegisterResponse(
            user_id=user.get("id"),
            email=user.get("email"),
            user=user,
            status="registered",
        )

    async def logout(
        self,
        claims=Depends(get_current_claims),            # richiede Authorization: Bearer <access_token>
        db: AsyncSession = Depends(get_db),
    ) -> LogoutResponse:
        """
        LOGOUT:
        - Revoca le sessioni/refresh token dell'utente corrente via Admin API.
        - L'access token in corso resta valido fino a scadenza → il client deve scartarlo.
        """
        user_id = claims.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token senza sub")

        res = await supabase_service.admin_logout_user(user_id)
        if res.get("error"):
            msg = res.get("message") or "Logout non riuscito"
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=msg)

        return LogoutResponse(ok=True)
