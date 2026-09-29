"""
Tests for the DocMind ingestion layer.

These tests avoid real embedding/model downloads. They verify the behavior of
the PDF extraction, chunking, hashing, and index-path helpers.
"""
import os
from types import SimpleNamespace

from langchain.schema import Document

from app import ingestion


def test_get_pdf_documents_extracts_page_metadata(monkeypatch):
    """A readable PDF page is converted into a Document with page metadata."""

    class FakePage:
        def __init__(self, text):
            self._text = text

        def extract_text(self):
            return self._text

    class FakeReader:
        def __init__(self, _file):
            self.pages = [
                FakePage("First page text."),
                FakePage("   "),  # blank page should be skipped
                FakePage("Third page text."),
            ]

    monkeypatch.setattr(ingestion, "PdfReader", FakeReader)

    pdf_file = SimpleNamespace(name="sample.pdf", size=1234)
    documents = ingestion.get_pdf_documents([pdf_file])

    assert len(documents) == 2

    assert documents[0].page_content == "First page text."
    assert documents[0].metadata == {
        "source": "sample.pdf",
        "page": 1,
        "total_pages": 3,
    }

    assert documents[1].page_content == "Third page text."
    assert documents[1].metadata["page"] == 3


def test_split_documents_creates_chunks_and_preserves_metadata():
    """Chunking produces chunks and keeps the original page metadata."""

    document = Document(
        page_content="This is a sentence. " * 80,
        metadata={
            "source": "sample.pdf",
            "page": 2,
            "total_pages": 10,
        },
    )

    chunks = ingestion.split_documents([document])

    assert chunks
    assert all(chunk.metadata["source"] == "sample.pdf" for chunk in chunks)
    assert all(chunk.metadata["page"] == 2 for chunk in chunks)
    assert all("chunk_index" in chunk.metadata for chunk in chunks)
    assert [chunk.metadata["chunk_index"] for chunk in chunks] == list(range(len(chunks)))


def test_compute_file_hash_is_deterministic_and_order_independent():
    """The file hash stays the same when the same files are supplied in a different order."""

    first = SimpleNamespace(name="a.pdf", size=100)
    second = SimpleNamespace(name="b.pdf", size=200)

    hash_one = ingestion.compute_file_hash([first, second])
    hash_two = ingestion.compute_file_hash([second, first])

    assert hash_one == hash_two
    assert len(hash_one) == 12


def test_get_index_path_uses_configured_store(monkeypatch):
    """Index paths are built below the configured FAISS store directory."""

    monkeypatch.setattr(ingestion, "FAISS_STORE_DIR", "test_faiss_store")

    assert ingestion.get_index_path("abc123") == os.path.join(
    "test_faiss_store", "abc123"
    )
