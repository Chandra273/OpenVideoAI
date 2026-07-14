from fastapi import FastAPI
import logging

from app.api.v1.routes import router as v1_router
from app.core.config import settings


app = FastAPI(title="Text-to-Video API")

app.include_router(v1_router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
def on_startup():
    # Basic startup logging — in production use a structured logger
    logging.getLogger("uvicorn.info").info(f"Starting in {settings.APP_ENV} environment")
    logging.getLogger("uvicorn.info").info(f"Downloads dir: {settings.DOWNLOADS_DIR}")
