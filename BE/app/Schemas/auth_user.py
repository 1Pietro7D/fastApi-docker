# app/Schemas/auth_user.py

from __future__ import annotations
from pydantic import BaseModel, EmailStr
from typing import Optional, Any
from uuid import UUID

# ✅ Schema per la creazione di un nuovo utente (input)
# Questo modello definisce i campi accettati quando un nuovo utente viene creato,
# ad esempio tramite l'endpoint POST /users.
class AuthUserCreate(BaseModel):
    email: EmailStr                  # email valida (verificata con validazione Pydantic)
    password: str                    # password in chiaro, che verrà poi gestita da Supabase
    user_meta: Optional[dict] = None # metadati personalizzati lato utente (JSON opzionale)
    app_meta: Optional[dict] = None  # metadati legati all'app (es. ruolo iniziale)
    banned_until: Optional[str] = None # opzionale: data fino a quando l'utente è bannato
    phone: Optional[str] = None      # numero di telefono opzionale

# ✅ Schema per l'aggiornamento di un utente (input parziale)
# Usato per gli endpoint di update, dove non tutti i campi sono obbligatori.
class AuthUserUpdate(BaseModel):
    email: Optional[EmailStr] = None         # possibilità di aggiornare l'email
    phone: Optional[str] = None              # possibilità di aggiornare il telefono
    banned_until: Optional[Any] = None       # possibilità di aggiornare lo stato di ban
    raw_app_meta_data: Optional[dict] = None # metadati applicativi grezzi (JSON completo)
    raw_user_meta_data: Optional[dict] = None # metadati utente grezzi (JSON completo)

# ✅ Schema di lettura di un utente (output)
# Definisce i campi che vengono restituiti nelle API in risposta (DTO read-only).
class AuthUserRead(BaseModel):
    id: UUID                                # identificatore univoco dell’utente (Supabase usa UUID)
    email: Optional[EmailStr] = None        # email dell’utente
    role: Optional[str] = None              # ruolo (es. admin, user, etc.)
    raw_app_meta_data: Optional[dict] = None# metadati applicativi (dati dal DB)
    raw_user_meta_data: Optional[dict] = None# metadati utente (dati dal DB)

    class Config:
        # Configurazione per permettere a Pydantic di leggere i dati
        # direttamente dagli oggetti ORM (SQLAlchemy) oltre che da dict.
        from_attributes = True
