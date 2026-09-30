"""Application configuration."""

from functools import lru_cache
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


BASE_DIR = Path(__file__).resolve().parents[2]


class Settings:
    """Centralized runtime configuration loaded from environment variables."""

    APP_NAME: str = os.getenv("APP_NAME", "DocMind API")
    API_V1_PREFIX: str = os.getenv("API_V1_PREFIX", "/api/v1")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    FAISS_STORE_DIR: Path = Path(
        os.getenv("FAISS_STORE_DIR", str(BASE_DIR / "data" / "faiss_store"))
    )

    EMBEDDING_MODEL: str = os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    )
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
    GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")

    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))

    SYSTEM_PROMPT: str = os.getenv(
        "SYSTEM_PROMPT",
        """You are a helpful AI assistant. Answer questions based ONLY on the
provided context documents. If the answer cannot be found in the context, respond with:
\"I couldn't find that information in the provided documents.\"
Be concise, accurate, and always ground your answer in the source material.""",
    )

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.FAISS_STORE_DIR.mkdir(parents=True, exist_ok=True)
    return settings
