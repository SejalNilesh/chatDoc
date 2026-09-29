"""
DocMind AI embedding model access.
"""

from langchain_community.embeddings import HuggingFaceEmbeddings

from .config import EMBEDDING_MODEL


def get_embeddings(cache=None) -> HuggingFaceEmbeddings:
    """
    Return cached HuggingFace embeddings model.

    `cache` is intentionally injectable so the UI can use Streamlit session
    state later, while the API can use a plain process-local dictionary.
    """
    if cache is not None:
        if "embeddings" not in cache:
            cache["embeddings"] = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        return cache["embeddings"]

    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
