# DocMind — Layered RAG Application

DocMind is a Streamlit frontend backed by a small FastAPI service layer.

## Structure

```text
chatDoc/
├── app/
│   ├── main.py
│   ├── api/routes/
│   ├── services/
│   ├── schemas/
│   └── core/
├── streamlit/
│   ├── app.py
│   ├── api_client.py
│   ├── htmlTemplates.py
│   └── code.css
├── tests/
├── data/faiss_store/
├── requirements.txt
├── ARCHITECTURE.md
└── README.md
```

## Run locally

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` from `.env.example` and add `GROQ_API_KEY`.

### Terminal 1 — FastAPI

```bash
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

### Terminal 2 — Streamlit

```bash
streamlit run streamlit/app.py
```

UI: http://localhost:8501

## API

- `GET /health`
- `POST /api/v1/documents/ingest`
- `POST /api/v1/documents/summary`
- `POST /api/v1/query`
