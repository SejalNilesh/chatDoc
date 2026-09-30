"""HTTP client for the DocMind FastAPI backend."""

from __future__ import annotations

from typing import Any

import requests


class APIClientError(RuntimeError):
    """Raised when the DocMind API cannot be reached or returns an error."""


class DocMindAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000", timeout: int = 300) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _post(self, path: str, **kwargs: Any) -> dict:
        try:
            response = requests.post(
                f"{self.base_url}{path}",
                timeout=kwargs.pop("timeout", self.timeout),
                **kwargs,
            )
        except requests.RequestException as exc:
            raise APIClientError(
                f"Could not connect to the DocMind API at {self.base_url}. "
                "Start the FastAPI server first."
            ) from exc

        try:
            payload = response.json()
        except ValueError:
            payload = {"detail": response.text or "Invalid API response."}

        if not response.ok:
            detail = payload.get("detail", "API request failed.")
            raise APIClientError(str(detail))

        if not isinstance(payload, dict):
            raise APIClientError("API returned an unexpected response format.")

        return payload

    def health(self) -> dict:
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=min(self.timeout, 10),
            )
            response.raise_for_status()
            payload = response.json()
            return payload if isinstance(payload, dict) else {"status": "unknown"}
        except (requests.RequestException, ValueError) as exc:
            raise APIClientError(
                f"Could not connect to the DocMind API at {self.base_url}."
            ) from exc

    def ingest(self, files: list[tuple[str, bytes, str]]) -> dict:
        multipart = [
            ("files", (filename, content, content_type))
            for filename, content, content_type in files
        ]
        return self._post(
            "/api/v1/documents/ingest",
            files=multipart,
            timeout=self.timeout,
        )

    def query(self, file_hash: str, question: str) -> dict:
        return self._post(
            "/api/v1/query",
            json={"file_hash": file_hash, "query": question},
            timeout=min(self.timeout, 120),
        )

    def summary(self, files: list[tuple[str, bytes, str]]) -> dict:
        multipart = [
            ("files", (filename, content, content_type))
            for filename, content, content_type in files
        ]
        return self._post(
            "/api/v1/documents/summary",
            files=multipart,
            timeout=min(self.timeout, 120),
        )
