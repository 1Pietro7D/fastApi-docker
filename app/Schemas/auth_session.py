# app/Schemas/auth_session.py

from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, EmailStr
from uuid import UUID

# --------- LOGIN ---------

class LoginInput(BaseModel):
    """Payload di input per login (password grant)."""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Risposta del login: token + info utente."""
    access_token: str
    token_type: str = "bearer"
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    user: dict[str, Any] = {}  # oggetto utente Supabase (id, email, ecc.)


# --------- REGISTER ---------

class RegisterInput(BaseModel):
    """Payload per registrazione utente."""
    email: EmailStr
    password: str
    user_meta: Optional[dict] = None   # metadati utente (profilo)
    app_meta: Optional[dict] = None    # metadati applicativi
    phone: Optional[str] = None        # telefono opzionale


class RegisterResponse(BaseModel):
    """Risposta della registrazione."""
    user_id: UUID
    email: Optional[EmailStr] = None
    user: dict[str, Any] = {}          # oggetto utente Supabase completo
    status: str = "registered"


# --------- LOGOUT ---------

class LogoutResponse(BaseModel):
    """Esito del logout."""
    ok: bool = True
