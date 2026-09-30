# DocMind Streamlit UI

The Streamlit application is the presentation layer. It communicates with the FastAPI backend over HTTP and does not import the RAG, FAISS, embedding, or LLM services.

## Run

From the project root:

```bash
streamlit run streamlit/app.py
```

Start the backend separately:

```bash
uvicorn app.main:app --reload
```

By default the UI connects to `http://localhost:8000`.

Set these optional environment variables in `.env`:

```env
DOCMIND_API_URL=http://localhost:8000
DOCMIND_API_TIMEOUT=300
```
