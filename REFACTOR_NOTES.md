# Refactor Notes

The original application mixed Streamlit presentation with document ingestion and RAG logic. The main change is to make Streamlit an API client and move the pipeline behind FastAPI.

## Before

```text
Streamlit
  └── PDF extraction
  └── chunking
  └── embeddings
  └── FAISS
  └── retrieval
  └── Groq
```

## After

```text
Streamlit → FastAPI routes → Services → FAISS / Embeddings / Groq
```

The refactor deliberately avoids adding controllers and repositories because this application has a small number of use cases and only one vector-store implementation.

The existing RAG settings are preserved: 1,000-character chunks, 200-character overlap, the `all-MiniLM-L6-v2` embedding model, MMR retrieval (`k=4`, `fetch_k=6`), and the configured Groq model.
