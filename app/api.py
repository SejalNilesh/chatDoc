"""
DocMind AI API layer.

Small FastAPI wrapper around the existing ingestion and retrieval logic.
The underlying RAG logic is kept in ingestion.py, embeddings.py, and
retrieval.py so the Streamlit UI does not own the pipeline.
"""

from io import BytesIO
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from .embeddings import get_embeddings
from .ingestion import (
    build_vectorstore,
    compute_file_hash,
    get_pdf_documents,
    load_vectorstore,
    save_vectorstore,
    split_documents,
)
from .retrieval import generate_summary, get_conversation_chain

load_dotenv()

app = FastAPI(title="DocMind API")

# Process-local caches are intentionally small for this assignment.
_embedding_cache = {}
_conversation_cache = {}


class QueryRequest(BaseModel):
    file_hash: str
    query: str


def _to_file_objects(files: List[UploadFile]) -> list:
    """Convert FastAPI uploads into file-like objects compatible with PdfReader."""
    file_objects = []
    for upload in files:
        content = upload.file.read()
        pdf = BytesIO(content)
        pdf.name = upload.filename
        pdf.size = len(content)
        file_objects.append(pdf)
    return file_objects


def _get_conversation(file_hash: str):
    """Load or create the in-memory conversation chain for a persisted index."""
    if file_hash in _conversation_cache:
        return _conversation_cache[file_hash]

    embeddings = get_embeddings(_embedding_cache)
    vectorstore = load_vectorstore(file_hash, embeddings)

    if vectorstore is None:
        raise HTTPException(
            status_code=404,
            detail="No indexed document set found for this file_hash. Ingest PDFs first.",
        )

    conversation = get_conversation_chain(vectorstore)
    _conversation_cache[file_hash] = conversation
    return conversation


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest")
async def ingest(files: List[UploadFile] = File(...)):
    """
    Extract, chunk, embed, and persist the uploaded PDFs.

    Existing file-hash behavior is preserved: the index is reused when the
    same uploaded filenames + sizes are seen again.
    """
    if not files:
        raise HTTPException(status_code=400, detail="Please upload at least one PDF.")

    pdf_files = _to_file_objects(files)
    file_hash = compute_file_hash(pdf_files)

    embeddings = get_embeddings(_embedding_cache)
    cached_vs = load_vectorstore(file_hash, embeddings)

    if cached_vs:
        vectorstore = cached_vs
        indexed_chunks = None
        status = "loaded_existing"
    else:
        docs = get_pdf_documents(pdf_files)
        if not docs:
            raise HTTPException(
                status_code=400,
                detail="No readable text found. Are these scanned PDFs?",
            )

        chunks = split_documents(docs)
        vectorstore = build_vectorstore(chunks, _embedding_cache)
        save_vectorstore(vectorstore, file_hash)

        indexed_chunks = len(chunks)
        status = "indexed"

    _conversation_cache[file_hash] = get_conversation_chain(vectorstore)

    response = {
        "file_hash": file_hash,
        "status": status,
        "files": [f.filename for f in files],
    }

    if indexed_chunks is not None:
        response["indexed_chunks"] = indexed_chunks

    return response


@app.post("/query")
def query(request: QueryRequest):
    """
    Run the existing conversational RAG flow and return the answer + sources.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    conversation = _get_conversation(request.file_hash)

    try:
        response = conversation({"question": request.query})
        source_docs = response.get("source_documents", [])

        sources = []
        seen = set()

        for doc in source_docs:
            meta = doc.metadata
            src = meta.get("source", "Unknown")
            page = meta.get("page", "?")
            key = f"{src}|{page}"

            if key in seen:
                continue

            seen.add(key)
            sources.append(
                {
                    "document": src,
                    "page": page,
                    "snippet": doc.page_content[:300].replace("\n", " ") + "…",
                }
            )

        return {
            "answer": response.get("answer", ""),
            "sources": sources,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating response: {e}",
        )


@app.post("/summary")
async def summary(files: List[UploadFile] = File(...)):
    """
    Expose the existing document-summary feature without changing its logic.
    """
    if not files:
        raise HTTPException(status_code=400, detail="Please upload at least one PDF.")

    pdf_files = _to_file_objects(files)
    return generate_summary(pdf_files)
