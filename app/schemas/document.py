"""Document-related API schemas."""

from pydantic import BaseModel, Field


class Source(BaseModel):
    document: str
    page: int | str
    snippet: str


class IngestResponse(BaseModel):
    file_hash: str
    status: str
    files: list[str]
    indexed_chunks: int | None = None


class SummaryResponse(BaseModel):
    concise_summary: str | None = None
    detailed_summary: str | None = None
    key_topics: list[str] = Field(default_factory=list)
    important_concepts: list[str] = Field(default_factory=list)
    error: str | None = None
