# DocMind Architecture

## Goal

Separate the Streamlit presentation layer from the RAG pipeline without adding abstractions that the current application does not need.

##
```text
                         ┌──────────────────────┐
                         │      Streamlit       │
                         │    UI / Web Client   │
                         └──────────┬───────────┘
                                    │ HTTP
                                    ▼
                         ┌──────────────────────┐
                         │       FastAPI        │
                         │      API Layer       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │        Routes        │
                         │                      │
                         │  documents.py        │
                         │  query.py            │
                         │  health.py           │
                         └───────┬───────┬──────┘
                                 │       │
                    ┌────────────┘       └─────────────┐
                    ▼                                  ▼
          ┌────────────────────┐             ┌────────────────────┐
          │  Ingestion Service │             │  Retrieval Service │
          └─────────┬──────────┘             └──────────┬─────────┘
                    │                                   │
                    │                                   │
                    ▼                                   ▼
          ┌────────────────────┐             ┌────────────────────┐
          │ Embedding Service  │             │ Embedding Service  │
          │ HuggingFace Model  │             │ Query Embedding    │
          └─────────┬──────────┘             └──────────┬─────────┘
                    │                                   │
                    │ document embeddings               │ query vector
                    ▼                                   ▼
          ┌────────────────────┐             ┌────────────────────┐
          │   FAISS Index      │◄────────────│    FAISS Search    │
          │   Vector Store     │             └─────────┬──────────┘
          └────────────────────┘                       │
                                                       │
                                              Relevant Chunks
                                              + Metadata / Sources
                                                       │
                                                       ▼
                                             ┌────────────────────┐
                                             │     Groq LLM       │
                                             │     Answer Gen     │
                                             └────────────────────┘


                    Summary Flow
          documents.py ──→ Summary Service ──→ Groq LLM
```

## Request flow

```text
Streamlit
   │ HTTP
   ▼
FastAPI
   │
   ├── routes
   │     ├── documents.py
   │     └── query.py
   │
   ▼
services
   ├── ingestion_service.py
   ├── retrieval_service.py
   ├── embedding_service.py
   ├── llm_service.py
   └── summary_service.py
   │
   ├── FAISS
   ├── HuggingFace Embeddings
   └── Groq
```

## Why this structure?

**Routes are HTTP-only.** They handle uploads, validation, status codes, and response schemas.

**Services contain application logic.** Ingestion, retrieval, embeddings, LLM calls, and summarization are independently testable responsibilities.

**Streamlit is a client.** It only handles the UI and calls the API through `streamlit/api_client.py`.

**No controller layer.** The application is small enough that `route → service` is clear and avoids a pass-through layer.

**No repository layer.** FAISS is currently the only persistence mechanism, so a repository abstraction would add indirection without solving a current requirement. FAISS load/save code stays close to the services that use it.

**Schemas remain explicit.** Pydantic request/response models document the API boundary and provide validation.

## RAG flow

1. PDFs are uploaded to the ingestion endpoint.
2. Pages are extracted with source/page metadata.
3. Text is recursively split into chunks.
4. HuggingFace embeddings are generated.
5. The FAISS index is persisted under `data/faiss_store/<file_hash>`.
6. A query loads the index, performs MMR retrieval, and sends the grounded context to Groq.
7. The API returns the answer and deduplicated source references.

## Current limitation

Embedding models and conversational chains are cached in the API process. That is fine for the current assignment. A multi-instance deployment would need shared state or an external vector/cache service.
