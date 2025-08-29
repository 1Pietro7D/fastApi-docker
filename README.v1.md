# 📘 README — Setup FastAPI (async + Postgres + Redis) su Windows

## ✅ Requisiti
- **Python 3.13**
- **pip 25.2**
- **Docker Desktop** (per Docker/Compose)
- **PowerShell** (consigliato)  

---

## 1️⃣ Ambiente virtuale (Windows)

```powershell
python -m venv venv
```
Crea un ambiente virtuale nella cartella `venv\`.

```powershell
.\venv\Scripts\Activate.ps1
```
Attiva il venv in PowerShell:
- modifica `PATH` → usa python/pip del venv  
- imposta `VIRTUAL_ENV`  
- aggiunge `(venv)` al prompt  

> Se PowerShell blocca lo script:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

In **cmd.exe** invece:  
```cmd
venv\Scripts\activate.bat
```

---

## 2️⃣ Versioni Python e pip

```powershell
python --version   # es. Python 3.13.x
pip --version      # es. pip 25.2
pip install --upgrade pip
```

---

## 3️⃣ Installazione dipendenze

```powershell
pip install "fastapi[standard]"
# FastAPI + uvicorn (con extras: uvloop, httptools, watchfiles),
# python-multipart, jinja2, pyyaml, itsdangerous
```

```powershell
pip install sqlalchemy[asyncio]
# SQLAlchemy 2.x async (AsyncSession, create_async_engine)
```

```powershell
pip install asyncpg
# Driver asincrono PostgreSQL
```

```powershell
pip install pydantic-settings
# Settings da variabili/env con Pydantic v2
```

```powershell
pip install python-dotenv
# Carica automaticamente variabili da .env (utile in sviluppo)
```

```powershell
pip install alembic
# Migrazioni database
```

```powershell
pip install redis
# Client Redis (caching, rate limiting, queue)
```

---

## 4️⃣ Gestione dipendenze

```powershell
pip list
```

```powershell
pip freeze > requirements.txt
# salva le versioni correnti in requirements.txt
```

```powershell
pip install -r requirements.txt
# ricrea l’ambiente con le stesse versioni
```

---

## 5️⃣ Struttura progetto

```powershell
mkdir app, app\api, app\api\v1, app\domain, app\domain\models, app\domain\repositories, app\infrastructure, app\infrastructure\repositories, app\schemas, app\services
```

```powershell
New-Item app\main.py -ItemType File
```

```powershell
Copy-Item .env.example .env
# copia e personalizza le variabili ambiente
```

---

## 6️⃣ Migrazioni con Alembic

```powershell
alembic init alembic
```

- In `alembic.ini` → configura `sqlalchemy.url` (o usa `DATABASE_URL` da `.env`)  
- In `alembic/env.py` → importa la tua `Base` e imposta `target_metadata = Base.metadata`  

```powershell
alembic revision -m "init" --autogenerate
alembic upgrade head
```

---

## 7️⃣ Avvio locale (sviluppo)

```powershell
uvicorn app.main:app --reload
```

- [http://127.0.0.1:8000/](http://127.0.0.1:8000/) → health  
- [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) → Swagger UI  
- [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc) → ReDoc  

---

## 8️⃣ Docker Compose

Assicurati che **Docker Desktop** sia avviato.  

```powershell
# Sviluppo (hot-reload, bind mount, porte aperte per debug)
docker compose up -d --build
# avvia app + Postgres + Redis (+ pgAdmin se incluso)
# Usa automaticamente docker-compose.yml + docker-compose.override.yml

# Produzione (immagine chiusa, niente bind mount, solo porta app)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

```

```powershell
docker compose logs -f app
# log dell’app FastAPI
```

```powershell
docker compose ps
# stato dei container
```

```powershell
docker compose exec app alembic upgrade head
# applica migrazioni nel container
```

```powershell
curl http://127.0.0.1:8000/
# test rapido → {"status":"ok"}
```

Stop:

```powershell
docker compose down     # ferma container (mantiene dati DB)
docker compose down -v  # rimuove anche volumi (reset DB)
```

---

## 9️⃣ Note operative (alto traffico)

- **Workers & pool DB**: dimensiona `pool_size`/`max_overflow` in base ai workers.  
  Esempio (Linux/prod):  
  ```bash
  gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000 app.main:app
  ```
- **Produzione**: niente `--reload`, niente volume bind → builda immagine finale.  
- **Caching**: Redis per query frequenti o rate limiting.  
- **Monitoraggio**: log strutturati, Prometheus, OpenTelemetry.  
- **Sicurezza**: CORS, limiti payload, validazione Pydantic.  
- **Task lenti**: Celery/RQ + Redis (non bloccare request HTTP).  
