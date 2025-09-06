# app/Infrastructure/db.py
from __future__ import annotations

from typing import AsyncGenerator
import ssl
import sys

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

from app.config import settings

Base = declarative_base()


def _make_ssl_context() -> dict:
    """
    Per asyncpg serve 'ssl': <SSLContext|bool>.
    - Se l'URL è asyncpg, costruiamo un SSLContext che usa il bundle CA di 'certifi'
      (evita errori su Windows dove il trust store può essere incompleto).
    - Se DB_SSL_VERIFY=false, usiamo un contesto che NON verifica (solo dev).
    """
    if "+asyncpg" not in settings.DATABASE_URL:
        return {}

    # bypass (solo dev)
    if settings.ENV != "prod" and not settings.DB_SSL_VERIFY:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return {"ssl": ctx}

    # verifica stretta con certifi
    try:
        import certifi  # type: ignore
        cafile = certifi.where()
        ctx = ssl.create_default_context(cafile=cafile)
        # opzionale: forza TLS 1.2+
        if hasattr(ssl, "PROTOCOL_TLS_CLIENT"):
            ctx.minimum_version = ssl.TLSVersion.TLSv1_2
        return {"ssl": ctx}
    except Exception:
        # fallback: ssl=True (usa store di sistema)
        return {"ssl": True}


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    connect_args=_make_ssl_context(),
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


# Utilità opzionali

async def check_connection() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


async def dispose_engine() -> None:
    await engine.dispose()
