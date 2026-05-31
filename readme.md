# 🧠 DocMind AI — Upgraded Multi-PDF RAG Chatbot

A portfolio-grade upgrade of the original MultiPDF Chat App.
All 10 improvements are implemented while keeping the original
Streamlit + LangChain + FAISS + Groq + HuggingFace architecture intact.

---

## Folder structure

```
chatDoc_upgraded/
├── app.py              ← main application (upgraded)
├── htmlTemplates.py    ← UI templates + global CSS (upgraded)
├── requirements.txt    ← pinned dependencies
├── .env                ← add your GROQ_API_KEY here (not committed)
└── faiss_store/        ← auto-created; stores persistent FAISS indexes
```

---

## Setup

```bash
pip install -r requirements.txt
echo "GROQ_API_KEY=your_key_here" > .env
streamlit run app.py
```

---

## What was upgraded (all 10 improvements)

### 1 · Source Citations + Page References
- `get_pdf_documents()` now returns `Document` objects with metadata:
  `source` (filename), `page` (1-based), `total_pages`, `chunk_index`.
- `ConversationalRetrievalChain` is built with `return_source_documents=True`.
- After every answer an expandable **📚 Source References** section shows
  citation cards: `📄 game.pdf | Page 5` + the relevant text snippet.

### 2 · Modern UI / UX
- Full dark theme with CSS variables (`--bg-primary`, `--accent-1`, etc.).
- Animated gradient top bar (shimmer effect).
- `Syne` (display) + `DM Sans` (body) font pairing — no generic fonts.
- Chat bubbles with avatar icons, gradient accents, smooth fade-in animations.
- Welcome screen with feature grid before any PDFs are loaded.
- Summary cards with tag pills for topics and concepts.
- All Streamlit default branding hidden.

### 3 · Persistent FAISS Vector Database
- `compute_file_hash()` creates an MD5 fingerprint from file names + sizes.
- `save_vectorstore()` calls `FAISS.save_local()` under `faiss_store/<hash>/`.
- `load_vectorstore()` calls `FAISS.load_local()` on re-upload of same files.
- Status messages: *"⚡ Loaded existing vector database"* vs *"✅ Indexed N chunks"*.

### 4 · Streaming Responses
- `ChatGroq` is initialised with `streaming=True`.
- After the chain returns, the answer is replayed character-by-character in
  `st.empty()` with a blinking cursor (`▌`), simulating real token streaming.
- Conversational memory is preserved across streamed turns.

### 5 · Recursive Chunking
- Replaced `CharacterTextSplitter` with `RecursiveCharacterTextSplitter`.
- Separators: `["\n\n", "\n", ". ", " ", ""]` — tries paragraph breaks first.
- `chunk_size=1000`, `chunk_overlap=200` (20% overlap).  
  *Why*: paragraph-aware splitting reduces mid-sentence breaks; 20% overlap
  ensures cross-boundary information is not lost.

### 6 · PDF Summarization
- **Generate Summary** button in the sidebar (appears after processing).
- Sends a representative text sample (~5 000 chars) to Groq with a
  JSON-structured prompt.
- Displays four sections in cards: *Quick Overview*, *Detailed Summary*,
  *Key Topics* (pill tags), *Important Concepts* (pill tags).

### 7 · Page-Aware Metadata Pipeline
- `get_pdf_documents()` iterates pages individually, attaching
  `{"source": filename, "page": page_num, "total_pages": N}` to each `Document`.
- `split_documents()` adds `chunk_index` after splitting so every chunk
  carries its origin.
- Metadata flows through FAISS and is available on `source_documents` at
  retrieval time.

### 8 · Better RAG Quality
- **MMR retrieval**: `search_type="mmr"`, `k=4`, `fetch_k=6`, `lambda_mult=0.6`.
  Balances relevance and diversity, reducing redundant chunks.
- **Custom system prompt** injected via `PromptTemplate`:
  *"If the answer cannot be found in the context, clearly say so."*
- `temperature=0.1` for factual grounding with minimal hallucination.

### 9 · Code Quality
- Every function has a docstring explaining its purpose.
- Constants are defined at the top (`CHUNK_SIZE`, `EMBEDDING_MODEL`, etc.).
- Corrupted/blank PDF pages are skipped with a `st.warning()` — no crash.
- `get_embeddings()` is cached in session state to avoid reload overhead.
- Clear separation: PDF processing → chunking → vectorstore → chain → UI.

### 10 · Full Output
All files are self-contained and ready to run.
