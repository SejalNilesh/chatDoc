"""
Tests for the DocMind FastAPI layer.

The API tests mock the underlying RAG conversation so no Groq call, FAISS
load, or embedding model download is required.
"""

from fastapi.testclient import TestClient

from app import api


client = TestClient(api.app)


def test_health_returns_200():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_query_returns_answer_and_deduplicated_sources(monkeypatch):
    """A valid query returns the answer plus page-aware source references."""

    class FakeConversation:
        def __call__(self, payload):
            assert payload == {"question": "What is RAG?"}

            doc_a = type(
                "Doc",
                (),
                {
                    "page_content": "RAG combines retrieval with generation.",
                    "metadata": {"source": "rag.pdf", "page": 4},
                },
            )()
            doc_a_duplicate = type(
                "Doc",
                (),
                {
                    "page_content": "Same page, another chunk.",
                    "metadata": {"source": "rag.pdf", "page": 4},
                },
            )()
            doc_b = type(
                "Doc",
                (),
                {
                    "page_content": "A second source page.",
                    "metadata": {"source": "rag.pdf", "page": 5},
                },
            )()

            return {
                "answer": "RAG retrieves relevant context before generation.",
                "source_documents": [doc_a, doc_a_duplicate, doc_b],
            }

    monkeypatch.setattr(api, "_get_conversation", lambda _file_hash: FakeConversation())

    response = client.post(
        "/query",
        json={"file_hash": "abc123", "query": "What is RAG?"},
    )

    assert response.status_code == 200

    payload = response.json()
    assert payload["answer"] == "RAG retrieves relevant context before generation."

    assert payload["sources"] == [
        {
            "document": "rag.pdf",
            "page": 4,
            "snippet": "RAG combines retrieval with generation.…",
        },
        {
            "document": "rag.pdf",
            "page": 5,
            "snippet": "A second source page.…",
        },
    ]


def test_query_rejects_empty_query():
    response = client.post(
        "/query",
        json={"file_hash": "abc123", "query": "   "},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Query cannot be empty."


def test_query_rejects_missing_index(monkeypatch):
    """The API returns 404 when a file hash has not been ingested."""

    from fastapi import HTTPException

    def fake_get_conversation(_file_hash):
        raise HTTPException(
            status_code=404,
            detail="No indexed document set found for this file_hash. Ingest PDFs first.",
        )

    monkeypatch.setattr(api, "_get_conversation", fake_get_conversation)

    response = client.post(
        "/query",
        json={"file_hash": "missing", "query": "Hello"},
    )

    assert response.status_code == 404
    assert "Ingest PDFs first" in response.json()["detail"]
