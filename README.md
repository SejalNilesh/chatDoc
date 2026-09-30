# DocMind — RAG-based Document Intelligence

DocMind is a document Q&A and summarization application built with a FastAPI backend, a Streamlit frontend, and a retrieval-augmented generation (RAG) pipeline powered by LangChain, FAISS, sentence-transformers, and Groq.

It lets you upload PDF documents, ingest them into a vector store, ask natural-language questions about the content, and receive grounded answers based on the document context.

## Features

- Upload one or more PDF files
- Extract and chunk document text
- Generate embeddings with sentence-transformers
- Store and retrieve vectors using FAISS
- Answer questions with a grounded RAG workflow
- Generate document summaries through the backend API
- Use a lightweight Streamlit UI for interaction

## Architecture

The project is split into a clean backend/frontend structure:

- FastAPI app for API routes, validation, and orchestration
- RAG services for ingestion, retrieval, embeddings, summarization, and LLM access
- Streamlit app as the presentation layer
- FAISS as the persistent vector index for document retrieval

## Tech Stack

- Python
- FastAPI
- Streamlit
- LangChain
- FAISS
- sentence-transformers
- Groq
- PyPDF2
- Pydantic

## Repository Structure

```text
chatDoc/
├── app/
│   ├── api/
│   │   └── routes/
│   ├── core/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── streamlit/
│   ├── app.py
│   ├── api_client.py
│   ├── htmlTemplates.py
│   └── code.css
├── data/
│   └── faiss_store/
├── tests/
├── .env.example
├── ARCHITECTURE.md
├── README.md
├── requirements.txt
└── REFACTOR_NOTES.md
```

## Getting Started

### 1) Clone the repository

```bash
git clone https://github.com/SejalNilesh/chatDoc.git
cd chatDoc
```

### 2) Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

On macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

### 4) Configure environment variables

Copy the example environment file and add your Groq API key:

```bash
cp .env.example .env
```

Then update `.env` with your credentials and settings:

```env
GROQ_API_KEY=your_groq_api_key
APP_NAME=DocMind API
ENVIRONMENT=development
FAISS_STORE_DIR=data/faiss_store
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
GROQ_MODEL=openai/gpt-oss-120b
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
DOCMIND_API_URL=http://localhost:8000
DOCMIND_API_TIMEOUT=300
```

## Run the Application

### Terminal 1 — Start the FastAPI backend

```bash
uvicorn app.main:app --reload
```

The API will be available at:

- Swagger docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Terminal 2 — Start the Streamlit UI

```bash
streamlit run streamlit/app.py
```

The UI will be available at:

- http://localhost:8501

## API Endpoints

The backend exposes the following endpoints:

- `GET /health`
- `POST /api/v1/documents/ingest`
- `POST /api/v1/documents/summary`
- `POST /api/v1/query`

### Example: ingest a PDF

```bash
curl -X POST "http://localhost:8000/api/v1/documents/ingest" \
  -F "files=@sample.pdf"
```

### Example: ask a question

```bash
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "file_hash": "<file_hash>",
    "query": "What are the key findings in this document?"
  }'
```

## Notes

- The application expects uploaded documents to be in PDF format.
- Generated FAISS indexes are stored under `data/faiss_store`.
- The project is designed for local development and small-scale document intelligence workflows.

## Additional Documentation

- `ARCHITECTURE.md` — project architecture and design decisions
- `REFACTOR_NOTES.md` — notes on refactoring and maintainability improvements

## License

This project is currently provided without a formal license file. If you plan to distribute or reuse it publicly, consider adding an appropriate open-source license.
