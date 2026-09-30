"""Query request/response schemas."""

from pydantic import BaseModel, Field, field_validator


class QueryRequest(BaseModel):
    file_hash: str = Field(min_length=1)
    query: str = Field(min_length=1)

    @field_validator("query")
    @classmethod
    def validate_query(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Query cannot be empty.")
        return value
