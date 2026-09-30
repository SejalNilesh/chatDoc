from fastapi.testclient import TestClient

from app.core.dependencies import get_retrieval_service
from app.main import app


def test_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_query_endpoint_uses_retrieval_service() -> None:
    class FakeRetrievalService:
        def ask(self, file_hash: str, query: str) -> dict:
            assert file_hash == "abc123"
            assert query == "What is this document about?"
            return {"answer": "A test answer.", "sources": []}

    app.dependency_overrides[get_retrieval_service] = lambda: FakeRetrievalService()
    try:
        client = TestClient(app)
        response = client.post(
            "/api/v1/query",
            json={
                "file_hash": "abc123",
                "query": "What is this document about?",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"answer": "A test answer.", "sources": []}
