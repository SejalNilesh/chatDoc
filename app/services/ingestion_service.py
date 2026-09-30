"""PDF ingestion: extraction, chunking, embeddings, and FAISS persistence."""

import hashlib
import logging
from collections.abc import Sequence
from io import BytesIO
from pathlib import Path

from PyPDF2 import PdfReader
from langchain.schema import Document
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import Settings
from app.core.exceptions import InvalidDocumentError
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class IngestionService:
    """Own the document-ingestion use case."""

    def __init__(self, settings: Settings, embedding_service: EmbeddingService) -> None:
        self.settings = settings
        self.embedding_service = embedding_service

    @staticmethod
    def compute_file_hash(pdf_files: Sequence[BytesIO]) -> str:
        """Preserve the existing name + size based cache identity."""
        hasher = hashlib.md5()
        for file_obj in sorted(
            pdf_files,
            key=lambda item: getattr(item, "name", str(item)),
        ):
            name = getattr(file_obj, "name", str(file_obj))
            size = getattr(file_obj, "size", 0)
            hasher.update(f"{name}:{size}".encode())
        return hasher.hexdigest()[:12]

    def extract_documents(self, pdf_files: Sequence[BytesIO]) -> list[Document]:
        documents: list[Document] = []

        for pdf_file in pdf_files:
            try:
                pdf_file.seek(0)
                reader = PdfReader(pdf_file)
                filename = getattr(pdf_file, "name", str(pdf_file))

                for page_num, page in enumerate(reader.pages, start=1):
                    page_text = page.extract_text()
                    if not page_text or not page_text.strip():
                        continue

                    documents.append(
                        Document(
                            page_content=page_text,
                            metadata={
                                "source": filename,
                                "page": page_num,
                                "total_pages": len(reader.pages),
                            },
                        )
                    )
            except Exception as exc:
                logger.warning(
                    "Could not parse %s: %s",
                    getattr(pdf_file, "name", pdf_file),
                    exc,
                )

        return documents

    def split_documents(self, documents: list[Document]) -> list[Document]:
        splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ". ", " ", ""],
            chunk_size=self.settings.CHUNK_SIZE,
            chunk_overlap=self.settings.CHUNK_OVERLAP,
            length_function=len,
        )
        chunks = splitter.split_documents(documents)

        for index, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = index

        return chunks

    def _index_path(self, file_hash: str) -> Path:
        return self.settings.FAISS_STORE_DIR / file_hash

    def _load_existing_index(self, file_hash: str, embeddings) -> FAISS | None:
        path = self._index_path(file_hash)
        if not (path / "index.faiss").exists():
            return None

        try:
            return FAISS.load_local(
                str(path),
                embeddings,
                allow_dangerous_deserialization=True,
            )
        except Exception as exc:
            logger.warning("Could not load saved FAISS index: %s", exc)
            return None

    def _save_index(self, vectorstore: FAISS, file_hash: str) -> None:
        path = self._index_path(file_hash)
        path.mkdir(parents=True, exist_ok=True)
        vectorstore.save_local(str(path))

    def ingest(self, pdf_files: Sequence[BytesIO]) -> dict:
        if not pdf_files:
            raise InvalidDocumentError("Please upload at least one PDF.")

        file_hash = self.compute_file_hash(pdf_files)
        embeddings = self.embedding_service.get_embeddings()

        cached = self._load_existing_index(file_hash, embeddings)
        if cached is not None:
            return {
                "file_hash": file_hash,
                "status": "loaded_existing",
                "files": [getattr(f, "name", "unknown") for f in pdf_files],
            }

        documents = self.extract_documents(pdf_files)
        if not documents:
            raise InvalidDocumentError(
                "No readable text found. Are these scanned PDFs?"
            )

        chunks = self.split_documents(documents)
        vectorstore = FAISS.from_documents(chunks, embeddings)
        self._save_index(vectorstore, file_hash)

        return {
            "file_hash": file_hash,
            "status": "indexed",
            "files": [getattr(f, "name", "unknown") for f in pdf_files],
            "indexed_chunks": len(chunks),
        }
