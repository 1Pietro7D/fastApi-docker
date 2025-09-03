from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.Router.routes import router
from app.config import settings

app = FastAPI(title=settings.APP_NAME)
# ✅ Configurazione CORS
origins = [
    "http://localhost:5173",  # Vite frontend in dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # domini autorizzati
    allow_credentials=True,
    allow_methods=["*"],            # GET, POST, PUT, DELETE ecc.
    allow_headers=["*"],            # Authorization, Content-Type ecc.
)

@app.get("/", tags=["health"])
async def health():
    return {"status": "ok"}

app.include_router(router)

