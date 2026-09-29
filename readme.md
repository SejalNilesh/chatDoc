# DocMind AI — Multi-PDF RAG Chatbot

DocMind is a multi-PDF Retrieval-Augmented Generation (RAG) chatbot that lets users upload PDFs, ask questions across them, view page-level source references, and generate document summaries.

The project was refactored to separate the Streamlit UI from the RAG pipeline. The core RAG behavior and existing features are preserved while the application is now exposed through a small FastAPI backend.

---

## Architecture

```text
                         ┌──────────────────────┐
                         │      Streamlit       │
                         │     UI / Client      │
                         └──────────┬───────────┘
                                    │ HTTP
                                    ▼
                         ┌──────────────────────┐
                         │       FastAPI        │
                         │      API Layer       │
                         └───────┬───────┬──────┘
                                 │       │
                            /ingest     /query
                                 │       │
                                 ▼       ▼
                         ┌──────────┐ ┌──────────────┐
                         │Ingestion │ │  Retrieval   │
                         │ Pipeline │ │  + LLM Chain │
                         └────┬─────┘ └──────┬───────┘
                              │              │
                              ▼              ▼
                         Embeddings        FAISS
                                             │
                                             ▼
                                            Groq
```

### Responsibilities

**Streamlit**
- User interaction and presentation
- PDF upload UI
- Chat interface
- Summary display
- Source citation display
- Calls the backend API

**FastAPI**
- API boundary between UI and RAG services
- Document ingestion endpoint
- Query endpoint
- Summary endpoint
- Health endpoint
- HTTP error handling

**Ingestion**
- PDF text extraction
- Page-aware metadata
- Recursive chunking
- File hashing
- FAISS persistence

**Retrieval**
- MMR retrieval
- Conversational RAG chain
- Groq LLM generation
- Source document collection
- PDF summarization

---

## Project Structure

```text
chatDoc/
│
├── app/
│   ├── __init__.py
│   ├── api.py
│   ├── config.py
│   ├── embeddings.py
│   ├── ingestion.py
│   └── retrieval.py
│
├── tests/
│   ├── test_api.py
│   ├── test_ingestion.py
│   └── test_retrieval.py
│
├── streamlit_app.py
├── htmlTemplates.py
├── code.css
├── requirements.txt
├── pytest.ini
├── readme.md
├── ARCHITECTURE.md
├── .env
└── faiss_store/
```

`faiss_store/` is created automatically and contains persisted FAISS indexes.

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Add your Groq API key

Create a `.env` file:

```env
GROQ_API_KEY=your_key_here
```

The application currently uses:

```text
openai/gpt-oss-120b
```

as the Groq model.

### 3. Start the FastAPI backend

From the project root:

```bash
uvicorn app.api:app --reload
```

The API runs at:

```text
http://localhost:8000
```

### 4. Start Streamlit

Open another terminal:

```bash
streamlit run streamlit_app.py
```

By default, Streamlit calls:

```text
http://localhost:8000
```

You can change the backend URL through:

```env
DOCMIND_API_URL=http://localhost:8000
```

---

## API Endpoints

### Health

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

### Ingest PDFs

```http
POST /ingest
```

The endpoint:

```text
PDF files
   ↓
Text extraction
   ↓
Page metadata
   ↓
Recursive chunking
   ↓
Embeddings
   ↓
FAISS
   ↓
Persisted index
```

The response includes the generated `file_hash`, files, and indexing status.

### Query documents

```http
POST /query
```

Request:

```json
{
  "file_hash": "abc123",
  "query": "What is the refund policy?"
}
```

Response:

```json
{
  "answer": "The refund policy allows...",
  "sources": [
    {
      "document": "policy.pdf",
      "page": 4,
      "snippet": "..."
    }
  ]
}
```

### Generate summary

```http
POST /summary
```

The endpoint exposes the existing PDF summary feature through the API.

---

## Features

### 1 · Source Citations + Page References

`get_pdf_documents()` creates LangChain `Document` objects with:

```text
source
page
total_pages
chunk_index
```

The retrieval chain returns source documents, and the UI shows expandable source-reference cards containing the filename, page number, and snippet.

### 2 · Modern UI / UX

- Minimal SaaS-style interface
- Custom CSS
- Chat bubbles with user/AI styling
- Welcome screen
- Summary cards
- Source citation cards
- Streamlit branding hidden

### 3 · Persistent FAISS Vector Database

- `compute_file_hash()` creates a fingerprint from uploaded filenames and sizes.
- FAISS indexes are persisted under `faiss_store/<hash>/`.
- Existing indexes can be loaded instead of rebuilding them for the same file set.

### 4 · Streaming-style Responses

The Groq client is configured for streaming.

The existing UI also preserves the character-by-character answer rendering behavior.

### 5 · Recursive Chunking

The application uses `RecursiveCharacterTextSplitter` with:

```text
chunk_size = 1000
chunk_overlap = 200
```

Separators:

```python
["\n\n", "\n", ". ", " ", ""]
```

### 6 · PDF Summarization

The sidebar provides a **Generate Summary** action.

The summary response contains:

```text
concise_summary
detailed_summary
key_topics
important_concepts
```

### 7 · Page-Aware Metadata Pipeline

Each PDF page is processed separately and keeps its source information through chunking and vector retrieval.

This makes it possible to show answers together with document/page references.

### 8 · MMR Retrieval

The retrieval configuration is:

```text
search_type = "mmr"
k = 4
fetch_k = 6
lambda_mult = 0.6
```

This retains the existing balance between relevance and diversity.

### 9 · Grounded Prompt

The RAG prompt instructs the model to answer only from the provided context and to explicitly state when the requested information cannot be found.

### 10 · Code Quality

- Functions include docstrings.
- Configuration constants are centralized.
- PDF parsing errors are handled without crashing the application.
- Embedding access is cached in the API process.
- UI and RAG responsibilities are separated.

---

## Testing

The project includes three test modules:

```text
tests/
├── test_api.py
├── test_ingestion.py
└── test_retrieval.py
```

Run the tests with:

```bash
python -m pytest -v
```

The current suite contains 11 tests covering:

### API
- Health endpoint
- Successful query response
- Source de-duplication
- Empty query validation
- Missing-index validation

### Ingestion
- PDF extraction
- Page metadata
- Blank-page handling
- Chunk creation
- Chunk metadata
- Deterministic file hashing
- FAISS index-path construction

### Retrieval
- Prompt construction
- MMR configuration
- Source-document return behavior
- Summary JSON parsing

---

## Design Decisions

### Why separate Streamlit and the RAG pipeline?

The UI should handle presentation and user interaction, while document processing and retrieval belong to the backend/service layer.

This makes the RAG logic independently testable and allows another frontend or client to call the API later.

### Why FastAPI?

FastAPI provides a small HTTP boundary around the existing Python RAG implementation without requiring unnecessary infrastructure.

### Why keep FAISS?

The refactor is focused on architecture rather than replacing the existing vector database. Keeping FAISS minimizes changes to the current RAG behavior while retaining persistent local indexes.

### Why keep the existing embedding model?

The refactor does not attempt to change retrieval quality or model selection. Keeping the existing embedding setup makes the architectural changes easier to evaluate independently.

### Why not over-engineer?

The current system is intentionally small:

```text
Streamlit → FastAPI → RAG services
```

Technologies such as Kafka, Redis, Celery, Kubernetes, or a managed vector database are not required for the current scope.

---

## Future Scaling

The current structure leaves room for future changes without requiring another complete rewrite.

For example:

```text
Current
Streamlit
   ↓
FastAPI
   ↓
Local FAISS

Future
Web Client
   ↓
Load Balancer
   ↓
Multiple API instances
   ↓
Shared Vector Database
   ↓
LLM Provider
```

Document ingestion could later become asynchronous:

```text
Upload
 ↓
API
 ↓
Background Job
 ↓
Ingestion Worker
 ↓
Embeddings
 ↓
Vector Database
```



---

## Features


- Multi-PDF chat
- Page-level source citations
- Persistent FAISS indexes
- Recursive chunking
- MMR retrieval
- Conversational memory
- Grounded prompt
- PDF summaries
- Streamlit UI
- Groq-based generation


