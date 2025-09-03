# 🚀 FastAPI MVC + Repository + ORM — Enterprise, con Supabase (DB + Auth via JWKS) — Windows

API REST **FastAPI** con architettura **MVC + Repository** e **SQLAlchemy async**, pronta per produzione:
- **DB**: PostgreSQL su **Supabase** (`asyncpg`, `sslmode=require`).
- **Auth**: **Supabase Auth** — il backend **verifica** JWT **RS256** via **JWKS** pubblica (niente password lato backend).
- **Uploads**: file (immagini/CSV/PDF) salvati su `app/Uploads/` e serviti statici via `/uploads/*` → nel DB salvi **solo l’URL**.
- **Qualità**: test `pytest`, Docker multi-stage + gunicorn, healthcheck, config pulita.

> Dev su **Windows (PowerShell)**; i container girano Linux (Docker Desktop).

---

## ✅ Requisiti
- **Python 3.13**, **pip 25.2**
- **Docker Desktop**
- **PowerShell**

---

## 🧱 Struttura
```
app/
├─ main.py
├─ config.py
├─ Infrastructure/
│  ├─ db.py
│  └─ jwks.py
├─ Models/
│  ├─ base.py
│  └─ user.py
├─ Schemas/
│  ├─ user.py
│  └─ auth.py
├─ Repositories/
│  ├─ user_repository.py
│  └─ user_sqlalchemy.py
├─ Services/
│  └─ user_service.py
├─ Controllers/
│  ├─ users_controller.py
│  └─ files_controller.py
├─ Router/
│  ├─ auth.py
│  └─ routes.py
├─ Utils/
│  ├─ pagination.py
│  └─ jwt_verify_supabase.py
└─ Uploads/
tests/
├─ conftest.py
└─ test_health.py
```

---

## 🔐 Supabase Auth (JWKS)
- Il login/registrazione avviene sul **client** tramite Supabase SDK.
- Il backend verifica `Authorization: Bearer <access_token_supabase>` con **firma RS256 + iss + aud** via JWKS.
- **Ruoli**: leggi da claim (es. `app_metadata.role`) o mappa `sub` → ruolo nel tuo DB.

---

## ⚙️ `.env` (usa `.env.example`)
```env
APP_NAME=My FastAPI App
ENV=dev

# --- Supabase Postgres ---
# Variante A: diretta (porta 5432) - semplice, adatta a pochi container
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:5432/DBNAME?sslmode=require

# Variante B: pooler TRANSACTION (porta 6543) - consigliata per ambienti auto-scalabili
# DATABASE_URL=postgresql+asyncpg://USER.PROJECT_REF:PASSWORD@POOLER_HOST:6543/postgres?sslmode=require

# Uploads
UPLOADS_DIR=app/Uploads
UPLOADS_URL_PREFIX=/uploads

# Supabase Auth JWKS
SUPABASE_PROJECT_URL=https://<PROJECT_REF>.supabase.co
SUPABASE_JWKS_URL=${SUPABASE_PROJECT_URL}/auth/v1/.well-known/jwks.json
TOKEN_ISSUER=${SUPABASE_PROJECT_URL}/auth/v1
TOKEN_AUDIENCE=authenticated
```

**Variante A vs B**
- **A (5432)**: +semplice; −rischio molte connessioni se hai molte repliche.
- **B (6543 pooler)**: +scalabile; −non ideale per feature che richiedono sessioni lunghe multi-transazione.

---

## ▶️ Setup rapido (Windows)
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
# (sviluppo) pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```
- Docs: `http://127.0.0.1:8000/docs`

---

## 🐳 Docker
- `docker-compose.yml` (base) → solo **app** (DB è Supabase).
- `docker-compose.override.yml` (dev) → bind mount + `--reload`.
- `docker-compose.prod.yml` (prod) → gunicorn + env prod + healthcheck.

```powershell
docker compose up -d --build
docker compose logs -f app
docker compose down

# Prod
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

---

## 🧪 Test
```powershell
pytest -q
pytest -q --cov=app --cov-report=term-missing
```

---

## 🛡️ Produzione
- **Gunicorn**: `-w` ≈ core (fino a 1.5× per I/O-bound), `timeout 60`, `max-requests 1000`.
- **Pool DB**: `(pool_size × workers) ≤ max_connections` lato Supabase.
- **Sicurezza**: CORS restrittivo, validazione Pydantic, HTTPS dietro reverse proxy.
- **Osservabilità**: log JSON, Prometheus, OpenTelemetry.
