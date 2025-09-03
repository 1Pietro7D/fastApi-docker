from fastapi import FastAPI
from app.Router.routes import router
from app.config import settings

app = FastAPI(title=settings.APP_NAME)

@app.get("/", tags=["health"])
async def health():
    return {"status": "ok"}

app.include_router(router)
