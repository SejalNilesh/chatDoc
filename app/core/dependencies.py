"""Shared application services used by FastAPI dependency injection."""

from typing import Any

from app.core.config import get_settings
from app.services.embedding_service import EmbeddingService
from app.services.ingestion_service import IngestionService
from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService
from app.services.summary_service import SummaryService


class AppServices:
    """Create long-lived service instances once per API process."""

    def __init__(self) -> None:
        settings = get_settings()
        self.embedding = EmbeddingService(settings)
        self.llm = LLMService(settings)
        self.ingestion = IngestionService(settings, self.embedding)
        self.retrieval = RetrievalService(settings, self.embedding, self.llm)
        self.summary = SummaryService(settings, self.llm)


services = AppServices()


def get_ingestion_service() -> IngestionService:
    return services.ingestion


def get_retrieval_service() -> RetrievalService:
    return services.retrieval


def get_summary_service() -> SummaryService:
    return services.summary


def get_health_details() -> dict[str, Any]:
    settings = get_settings()
    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
    }
