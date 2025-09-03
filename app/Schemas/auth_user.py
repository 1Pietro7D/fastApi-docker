from __future__ import annotations
from pydantic import BaseModel, EmailStr
from typing import Optional, Any
from uuid import UUID

class AuthUserCreate(BaseModel):
    email: EmailStr
    password: str
    user_meta: Optional[dict] = None
    app_meta: Optional[dict] = None
    banned_until: Optional[str] = None
    phone: Optional[str] = None

class AuthUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    banned_until: Optional[Any] = None
    raw_app_meta_data: Optional[dict] = None
    raw_user_meta_data: Optional[dict] = None

class AuthUserRead(BaseModel):
    id: UUID
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    raw_app_meta_data: Optional[dict] = None
    raw_user_meta_data: Optional[dict] = None

    class Config:
        from_attributes = True
