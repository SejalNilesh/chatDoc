"""API response schemas."""

from pydantic import BaseModel

from app.schemas.document import Source


class QueryResponse(BaseModel):
    answer: str
    sources: list[Source]


class HealthResponse(BaseModel):
    status: str
    environment: str
