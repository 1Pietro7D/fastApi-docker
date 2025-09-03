# 🚀 FastAPI MVC + Repository (async) — Supabase DB + Auth (JWKS)

Backend **FastAPI** interamente **asincrono** con architettura **MVC + Repository** e **SQLAlchemy 2.0 async**.

- **DB**: PostgreSQL su **Supabase** (`asyncpg`, `sslmode=require`)
- **Auth seria**: verifica **JWT RS256** via **JWKS** di Supabase (offline, scalabile)
- **Modello dati**: `auth.users` (di Supabase) + `public.roles` + **ponte** `public.user_roles`
- **CRUD Users**: lista, dettaglio, crea (via **service** Supabase), aggiorna, elimina
- **Qualità**: test `pytest`/`pytest-asyncio`/`httpx`, separazione conf/ambienti
- **Niente Docker** in questa versione (solo comandi locali Windows)

---

## ✅ Requisiti
- **Python 3.13**
- **pip 25.2**
- **PowerShell** (Windows)

---

## 🧱 Struttura del progetto
mkdir app, app\Infrastructure, app\Models, app\Schemas, app\Repositories, app\Services, app\Controllers, app\Router, app\Utils, tests, db, db\sql

```
app/
├─ main.py                         # Entrypoint FastAPI
├─ config.py                       # Settings (env, DB, JWKS)
├─ Infrastructure/
│  ├─ db.py                        # Engine/session SQLAlchemy async (Supabase)
│  ├─ jwks.py                      # Fetch JWKS (cache)
│  └─ supabase_service.py          # Service per signup/patch via Admin API (async httpx)
├─ Models/
│  ├─ auth_user.py                 # Mappatura auth.users (schema=auth)
│  ├─ role.py                      # public.roles
│  └─ user_role.py                 # public.user_roles (ponte)
├─ Schemas/
│  ├─ auth_user.py                 # Pydantic (read/update sicuro per auth.users)
│  ├─ role.py                      # Pydantic per roles
│  └─ user_role.py                 # Pydantic per assegnazioni
├─ Repositories/
│  ├─ auth_user_repository.py      # Repo async su auth.users (read/update/delete)
│  ├─ role_repository.py           # Repo async su roles
│  └─ user_role_repository.py      # Repo async su user_roles (ponte)
├─ Services/
│  ├─ user_service.py              # Business utenti (usa repo + supabase_service)
│  └─ role_service.py              # Business ruoli/assegnazioni
├─ Controllers/
│  ├─ users_controller.py          # CRUD utenti (lista/dettaglio/update/delete + create via service)
│  ├─ roles_controller.py          # CRUD ruoli
│  └─ user_roles_controller.py     # Assegna/rimuovi ruoli
├─ Router/
│  ├─ auth.py                      # Dependency: verifica JWT via JWKS + require_roles(["admin"])
│  └─ routes.py                    # Registro centralizzato rotte (prefix /api/v1)
└─ Utils/
   ├─ jwt_verify_supabase.py       # Verifica RS256 con JWKS
   └─ pagination.py                # utilità generiche

db/
└─ sql/
   └─ 001_roles.sql                # DDL per public.roles + public.user_roles (FK → auth.users)

tests/
├─ conftest.py                     # Lifespan app + AsyncClient httpx
├─ test_health.py                  # Smoke test “/”
├─ test_roles.py                   # Test CRUD ruoli (admin)
└─ test_users_crud.py              # Test CRUD utenti
```

---

## 📁 Crea la struttura (Windows / PowerShell)

> **Copia & incolla** in PowerShell nella cartella del progetto.

```powershell
# 1) Cartelle
$dirs = @(
  "app","app\Infrastructure","app\Models","app\Schemas","app\Repositories",
  "app\Services","app\Controllers","app\Router","app\Utils",
  "db\sql","tests"
)
$dirs | ForEach-Object { New-Item -ItemType Directory -Force -Path $_ | Out-Null }

# 2) Package markers (facoltativi ma consigliati)
$pkgs = @(
  "app\__init__.py","app\Infrastructure\__init__.py","app\Models\__init__.py",
  "app\Schemas\__init__.py","app\Repositories\__init__.py","app\Services\__init__.py",
  "app\Controllers\__init__.py","app\Router\__init__.py","app\Utils\__init__.py"
)
$pkgs | ForEach-Object { New-Item -ItemType File -Force -Path $_ | Out-Null }

# 3) File principali (vuoti, li riempirai col codice)
$files = @(
  "app\main.py","app\config.py",
  "app\Infrastructure\db.py","app\Infrastructure\jwks.py","app\Infrastructure\supabase_service.py",
  "app\Models\auth_user.py","app\Models\role.py","app\Models\user_role.py",
  "app\Schemas\auth_user.py","app\Schemas\role.py","app\Schemas\user_role.py",
  "app\Repositories\auth_user_repository.py","app\Repositories\role_repository.py","app\Repositories\user_role_repository.py",
  "app\Services\user_service.py","app\Services\role_service.py",
  "app\Controllers\users_controller.py","app\Controllers\roles_controller.py","app\Controllers\user_roles_controller.py",
  "app\Router\auth.py","app\Router\routes.py",
  "app\Utils\jwt_verify_supabase.py","app\Utils\pagination.py",
  "db\sql\001_roles.sql",
  "tests\conftest.py","tests\test_health.py","tests\test_roles.py","tests\test_users_crud.py",
  ".env.example","requirements.txt","pytest.ini"
)
$files | ForEach-Object { New-Item -ItemType File -Force -Path $_ | Out-Null }
```

> Dopo aver creato i file, incolla il **codice** che ti ho fornito nei relativi percorsi (o chiedimi di rigenerarli qui).

---

## ⚙️ Variabili d’ambiente (`.env`)
Crea `.env` (puoi partire da `.env.example`):

```env
APP_NAME=My FastAPI App
ENV=dev

# Supabase Postgres (usa SEMPRE sslmode=require)
DATABASE_URL=postgresql+asyncpg://USER:PASSWORD@HOST:5432/DBNAME?sslmode=require

# Supabase Auth (JWKS)
SUPABASE_PROJECT_URL=https://<PROJECT_REF>.supabase.co
SUPABASE_JWKS_URL=${SUPABASE_PROJECT_URL}/auth/v1/.well-known/jwks.json
TOKEN_ISSUER=${SUPABASE_PROJECT_URL}/auth/v1
TOKEN_AUDIENCE=authenticated

# Supabase Admin (service) — usato SOLO per creare/patchare utenti
SUPABASE_KEY=<SERVICE_ROLE_OR_ANON_KEY>   # per patch admin serve SERVICE ROLE
```

---

## 📦 Dipendenze

### requirements.txt
```txt
fastapi[standard]==0.116.1
SQLAlchemy[asyncio]==2.0.43
asyncpg==0.30.0
pydantic-settings==2.10.1
python-dotenv==1.1.1
python-jose[cryptography]==3.3.0
httpx==0.27.2
pytest==8.2.2
pytest-asyncio==0.23.8
asgi-lifespan==2.1.0
pytest-cov==5.0.0
```

**Setup ambiente**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

---

## ▶️ Avvio (dev)

```powershell
uvicorn app.main:app --reload
# Docs: http://127.0.0.1:8000/docs
```

**Autorizzazione**  
Proteggi le rotte admin con `Authorization: Bearer <access_token_supabase>` (ottenuto da Supabase Auth).  
La dependency `require_roles(["admin"])` verifica il token via JWKS e controlla nel DB l’associazione ruolo.

---

## 🗃️ Modello dati (riassunto)

- `auth.users` (gestita da Supabase) — **non** la creiamo noi.
- `public.roles`: elenco ruoli app → (id, name, description)
- `public.user_roles`: ponte utente↔ruolo → (user_id UUID → auth.users.id, role_id → roles.id, UNIQUE)

**DDL iniziale**: `db/sql/001_roles.sql`

---

## 🧩 CRUD Utenti

- `GET    /api/v1/users` — lista
- `GET    /api/v1/users/{user_id}` — dettaglio
- `POST   /api/v1/users` — **crea** via `Infrastructure/supabase_service.py` (signup + patch)
- `PUT    /api/v1/users/{user_id}` — aggiorna campi “safe” (email/phone/ban/meta)
- `DELETE /api/v1/users/{user_id}` — elimina (consigliato passare da Admin API)

> Tutto **async** (FastAPI + SQLAlchemy + httpx).

---

## 🧪 Test

- `tests/conftest.py` — avvio app in test con lifespan e `httpx.AsyncClient`
- `tests/test_health.py` — verifica `/`
- `tests/test_roles.py` — CRUD ruoli (richiede token admin o mocking)
- `tests/test_users_crud.py` — CRUD utenti (mock del service o ambiente di test Supabase)

Esecuzione:
```powershell
pytest -q
pytest -q --cov=app --cov-report=term-missing
```

---

## ℹ️ Note
- **RLS policy**: opzionali ma raccomandate se prevedi accessi diretti da client/Supabase SDK.
- **Service Admin**: usa la **service role key** SOLO lato backend e SOLO dove serve (creazione/patch utente), non esporla mai al client.
