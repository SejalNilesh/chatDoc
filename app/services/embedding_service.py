"""Embedding model service."""

from langchain_community.embeddings import HuggingFaceEmbeddings

from app.core.config import Settings


class EmbeddingService:
    """Create and cache the embedding model for the API process."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._embeddings: HuggingFaceEmbeddings | None = None

    def get_embeddings(self) -> HuggingFaceEmbeddings:
        if self._embeddings is None:
            self._embeddings = HuggingFaceEmbeddings(
                model_name=self.settings.EMBEDDING_MODEL
            )
        return self._embeddings
