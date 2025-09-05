# app/config.py

from typing import Optional
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    # Accetta campi extra nel .env e usa .env di default
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    DB_SSL_VERIFY: bool = True  # True=verifica CA (consigliato), False=disabilita verifica (solo dev)

    APP_NAME: str = "My FastAPI App"
    ENV: str = "dev"

    # Opzione 1: URL completo già pronto
    DATABASE_URL: Optional[str] = Field(default=None, description="postgresql+asyncpg://user:pass@host:5432/db?sslmode=require")

    # Opzione 2: componenti singoli (se non fornisci DATABASE_URL)
    DB_HOST: Optional[str] = None
    DB_NAME: Optional[str] = None
    DB_USER: Optional[str] = None
    DB_PASS: Optional[str] = None
    DB_PORT: Optional[int] = 5432
    DB_CHARSET: Optional[str] = "utf8"

    # Supabase Auth (JWKS)
    SUPABASE_PROJECT_URL: str
    SUPABASE_JWKS_URL: str
    TOKEN_ISSUER: str
    TOKEN_AUDIENCE: str

    # Supabase Admin key (service/anon)
    SUPABASE_KEY: str

    def assemble_db_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if not (self.DB_HOST and self.DB_NAME and self.DB_USER and self.DB_PASS):
            raise ValueError("Devi impostare DATABASE_URL oppure tutte le variabili DB_*")
        user = self.DB_USER
        pwd = quote_plus(self.DB_PASS)
        return f"postgresql+asyncpg://{user}:{pwd}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?sslmode=require"


settings = Settings()
# Normalizza: garantiamo che DATABASE_URL sia sempre valorizzato
settings.DATABASE_URL = settings.assemble_db_url()
