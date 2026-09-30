"""DocMind FastAPI application entry point."""

from fastapi import FastAPI
from dotenv import load_dotenv

from app.api.routes.documents import router as documents_router
from app.api.routes.health import router as health_router
from app.api.routes.query import router as query_router
from app.core.config import get_settings
from app.core.logging import configure_logging

load_dotenv()
configure_logging()
settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Document Q&A and summarization API powered by RAG.",
)


@app.get("/", tags=["health"])
def root() -> dict[str, str]:
    return {
        "name": settings.APP_NAME,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


app.include_router(health_router)
app.include_router(documents_router, prefix=settings.API_V1_PREFIX)
app.include_router(query_router, prefix=settings.API_V1_PREFIX)
