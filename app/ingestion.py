"""
DocMind AI ingestion pipeline.

The functions here are the original PDF extraction, chunking, hashing,
FAISS persistence, and vector-store construction logic moved out of the
Streamlit UI layer.
"""

import hashlib
import os

from PyPDF2 import PdfReader
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import CHUNK_OVERLAP, CHUNK_SIZE, FAISS_STORE_DIR
from .embeddings import get_embeddings


# ─── PDF Processing ────────────────────────────────────────────────────────────

def get_pdf_documents(pdf_files: list, warning_callback=None) -> list[Document]:
    """
    Extract text from PDFs while preserving page-level metadata.
    Returns a list of LangChain Document objects (one per page).
    Improvement #7: Page-aware metadata pipeline.
    """
    documents = []
    for pdf_file in pdf_files:
        try:
            reader = PdfReader(pdf_file)
            filename = getattr(pdf_file, "name", str(pdf_file))
            for page_num, page in enumerate(reader.pages, start=1):
                page_text = page.extract_text()
                if not page_text or not page_text.strip():
                    continue  # skip blank/image-only pages
                doc = Document(
                    page_content=page_text,
                    metadata={
                        "source": filename,
                        "page": page_num,
                        "total_pages": len(reader.pages),
                    }
                )
                documents.append(doc)
        except Exception as e:
            message = f"Could not parse {getattr(pdf_file, 'name', pdf_file)}: {e}"
            if warning_callback is not None:
                warning_callback(message)
    return documents


def split_documents(documents: list[Document]) -> list[Document]:
    """
    Split documents into chunks using RecursiveCharacterTextSplitter.
    Metadata is preserved per chunk. (Improvements #5, #7)
    """
    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", " ", ""],
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    chunks = splitter.split_documents(documents)
    # Attach chunk index to metadata
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = i
    return chunks


# ─── FAISS Persistence ─────────────────────────────────────────────────────────

def compute_file_hash(pdf_files: list) -> str:
    """Create a deterministic hash for a set of uploaded files (by name + size)."""
    hasher = hashlib.md5()
    for f in sorted(pdf_files, key=lambda x: getattr(x, "name", str(x))):
        name = getattr(f, "name", str(f))
        size = getattr(f, "size", 0)
        hasher.update(f"{name}:{size}".encode())
    return hasher.hexdigest()[:12]


def get_index_path(file_hash: str) -> str:
    return os.path.join(FAISS_STORE_DIR, file_hash)


def save_vectorstore(vectorstore: FAISS, file_hash: str) -> None:
    """Persist FAISS index to disk. (Improvement #3)"""
    path = get_index_path(file_hash)
    os.makedirs(path, exist_ok=True)
    vectorstore.save_local(path)


def load_vectorstore(file_hash: str, embeddings, warning_callback=None) -> FAISS | None:
    """Load existing FAISS index if available. (Improvement #3)"""
    path = get_index_path(file_hash)
    if os.path.exists(os.path.join(path, "index.faiss")):
        try:
            vs = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
            return vs
        except Exception as e:
            message = f"Could not load saved index ({e}); rebuilding…"
            if warning_callback is not None:
                warning_callback(message)
    return None


def build_vectorstore(chunks: list[Document], cache=None) -> FAISS:
    """Build FAISS vectorstore from document chunks."""
    embeddings = get_embeddings(cache)
    return FAISS.from_documents(chunks, embeddings)
