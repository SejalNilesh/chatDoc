"""Health-check endpoint."""

from fastapi import APIRouter

from app.core.dependencies import get_health_details
from app.schemas.response import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(**get_health_details())
