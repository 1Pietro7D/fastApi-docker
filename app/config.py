# app/config.py

from typing import Optional
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """
    Configurazione centralizzata dell'app.
    - Usa SOLO la Service Key (SUPABASE_KEY) per tutte le chiamate (signup, login, admin).
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Ambiente / App
    APP_NAME: str = "My FastAPI App"
    ENV: str = "dev"  # dev | prod

    # SSL DB
    DB_SSL_VERIFY: bool = True

    # Connessione DB
    DATABASE_URL: Optional[str] = Field(
        default=None,
        description="postgresql+asyncpg://user:pass@host:5432/db?sslmode=require",
    )
    DB_HOST: Optional[str] = None
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASS: Optional[str] = None
    DB_PORT: Optional[int] = 5432
    DB_CHARSET: Optional[str] = "utf8"

    # Supabase Auth
    SUPABASE_PROJECT_URL: str
    SUPABASE_JWKS_URL: str
    TOKEN_ISSUER: str
    TOKEN_AUDIENCE: str

    # Solo service key
    SUPABASE_KEY: str

    AUTH_AUTO_CONFIRM_DEV: bool = True

    def assemble_db_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if not (self.DB_HOST and self.DB_NAME and self.DB_USER and self.DB_PASS):
            raise ValueError("Devi impostare DATABASE_URL oppure tutte le variabili DB_*")
        user = self.DB_USER
        pwd = quote_plus(self.DB_PASS)
        return f"postgresql+asyncpg://{user}:{pwd}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?sslmode=require"


settings = Settings()
settings.DATABASE_URL = settings.assemble_db_url()
