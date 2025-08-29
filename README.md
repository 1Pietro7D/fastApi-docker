# 📘 Documentazione Progetto FastAPI (MVC + Repository + ORM)

## ✅ Obiettivi
- Architettura **MVC** con **pattern Repository**.  
- **SQLAlchemy async** come ORM.  
- Router centralizzato: ogni rotta definisce **URL, controller, autenticazione e ruoli**.  
- **Uploads** di file (immagini, CSV, PDF) salvati su disco (`app/Uploads/`), con **URL salvato nel DB** e file serviti come statici.  
- Ambiente gestito con **Docker Compose** (Postgres, Redis, FastAPI, pgAdmin).  
- Separazione tra **sviluppo** (hot-reload, bind mount) e **produzione** (immagine chiusa, gunicorn workers).

---

## 📦 Librerie usate
- **FastAPI [standard]** → web framework + server ASGI (uvicorn, httptools, uvloop, ecc.).  
- **SQLAlchemy [asyncio]** → ORM asincrono.  
- **asyncpg** → driver PostgreSQL asincrono.  
- **pydantic-settings** → configurazione tipizzata da env/.env.  
- **python-dotenv** → carica file `.env` (solo sviluppo).  
- **alembic** → migrazioni database.  
- **redis** → client Redis (cache, rate limiting, code).  

---

## 🏗️ Struttura del progetto
```
app/
├─ main.py              # entrypoint FastAPI
├─ config.py            # settings globali
├─ Infrastructure/      # infrastruttura tecnica (DB, Redis, email, ecc.)
│  └─ db.py
├─ Models/              # ORM models (SQLAlchemy)
│  ├─ base.py
│  └─ user.py
├─ Schemas/             # Schemi Pydantic (input/output API)
│  ├─ user.py
│  └─ auth.py
├─ Repositories/        # Pattern Repository
│  ├─ user_repository.py
│  └─ user_sqlalchemy.py
├─ Services/            # Business logic
│  └─ user_service.py
├─ Controllers/         # Logica API (usa Services)
│  ├─ users_controller.py
│  └─ files_controller.py
├─ Router/              # Router centralizzato + auth/roles
│  ├─ auth.py
│  └─ routes.py
├─ Utils/               # utility comuni
│  ├─ hashing.py
│  └─ pagination.py
└─ Uploads/             # cartella file caricati
```

---

## 📂 Ruolo delle cartelle

- **Infrastructure/** → dettagli tecnici (DB engine, Redis client, integrazioni esterne).  
- **Models/** → definizione entità (ORM).  
- **Schemas/** → validazione input/output API (Pydantic).  
- **Repositories/** → accesso ai dati (contratto + implementazione SQLAlchemy).  
- **Services/** → logica di business, usa i repository.  
- **Controllers/** → orchestrano le richieste HTTP, dipendenze e risposte.  
- **Router/** → registra tutte le rotte con: path, metodo, controller, auth e ruoli.  
- **Utils/** → funzioni comuni (hashing, pagination, ecc.).  
- **Uploads/** → cartella per file caricati (servita come static path).  

---

## 🔄 Flow delle richieste (esempio `/api/v1/users`)
1. **Router** → definisce che `/users` (POST) va a `UsersController.create_user`, richiede auth ruolo `admin`.  
2. **Controller** → riceve input validato (schema), chiama `UserService`.  
3. **Service** → applica logica (es. check email univoca), usa `UserRepository`.  
4. **Repository** → interroga il DB tramite SQLAlchemy async.  
5. **Model** → mappa il risultato.  
6. **Schema** → converte entità in JSON di output.  

---

## 🔑 Autenticazione e Ruoli
- Dipendenza `require_auth(roles=[...])` applicata automaticamente dal Router.  
- Attualmente demo: header `X-Role` (`admin`, `manager`, `user`).  
- In produzione → sostituibile con JWT/OAuth2 senza cambiare Controller/Router.  

---

## 📂 Uploads
- Endpoint `/api/v1/files/upload` → salva file in `app/Uploads/`.  
- Restituisce `{"url": "/uploads/<nomefile>"}`.  
- FastAPI serve `/uploads/*` come **static files**.  
- Nel DB salvi solo l’URL, non il file binario.  

---

## ⚙️ Configurazione
### `.env`
```env
APP_NAME=My FastAPI App
ENV=dev

POSTGRES_USER=appuser
POSTGRES_PASSWORD=apppass
POSTGRES_DB=appdb
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://appuser:apppass@db:5432/appdb

DB_POOL_SIZE=20
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30
DB_POOL_RECYCLE=1800

UPLOADS_DIR=app/Uploads
UPLOADS_URL_PREFIX=/uploads

PGADMIN_DEFAULT_EMAIL=admin@example.com
PGADMIN_DEFAULT_PASSWORD=admin
```

---

## 🐳 Docker Compose

### File principali
- `docker-compose.yml` → definizione base (app + db + redis + pgAdmin).  
- `docker-compose.override.yml` → dev (bind mount, `--reload`, porte aperte per db/redis).  
- `docker-compose.prod.yml` → prod (gunicorn, niente bind, db/redis interni).  
- `Dockerfile` → immagine base Python 3.13.  
- `.env.example` → template delle variabili.

### Healthcheck
- **app** → `curl http://localhost:8000/`  
- **db** → `pg_isready -U $POSTGRES_USER`  
- **redis** → `redis-cli ping`

---

## ▶️ Avvio

### Dev (hot reload)
```powershell
docker compose up -d --build
# usa docker-compose.yml + docker-compose.override.yml
```

### Prod
```powershell
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

---

## 🧑‍💻 Avvio locale senza Docker
```powershell
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

---

## ⚡ Best Practices (alto traffico)

- **Workers**: `gunicorn -w N -k uvicorn.workers.UvicornWorker`  
  - N ≈ n° core CPU (fino a 1.5× se I/O-bound).  
- **Connection Pool**: `(pool_size × workers) ≤ max_connections PostgreSQL`.  
- **Cache Redis**: usa per query frequenti, invalidazione su update.  
- **Migrazioni**: sempre con `alembic revision --autogenerate` + `alembic upgrade head`.  
- **Logging/Monitoring**: log JSON, Prometheus metrics, OpenTelemetry tracing.  
- **Sicurezza**: CORS limitato, validazione Pydantic, limiti payload, upload sicuri.  
- **Task lenti**: spostati su Celery/RQ con Redis (non bloccare request).  

---

## 📌 Esempio API

### Creazione utente
```http
POST /api/v1/users
Headers:
  X-Role: admin
Body:
{
  "email": "alice@example.com",
  "full_name": "Alice Rossi",
  "role": "manager"
}
```

### Upload file
```http
POST /api/v1/files/upload
Headers:
  X-Role: user
Body (multipart/form-data):
  file=@report.pdf
```
Risposta:
```json
{"url": "/uploads/20250302123456_report.pdf", "filename": "20250302123456_report.pdf"}
```

---

## 🔮 Estensioni future
- Sostituire header `X-Role` con **JWT/OAuth2**.  
- Aggiungere repository per altre entità (es. `Product`, `Order`).  
- Aggiungere **service layer Redis** per caching avanzata.  
- Deploy con **Kubernetes** (Compose → Helm chart).  
