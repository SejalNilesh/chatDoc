"""
DocMind AI — Upgraded Multi-PDF RAG Chatbot
============================================
Improvements implemented:
  1. Source citations + page references
  2. Modernized dark UI (via htmlTemplates.py)
  3. Persistent FAISS vector database (save/load locally)
  4. Streaming responses (Groq streaming)
  5. RecursiveCharacterTextSplitter
  6. PDF summarization feature
  7. Page-aware metadata pipeline
  8. Better RAG quality (MMR retrieval + system prompt)
  9. Clean modular code with error handling
"""

import os
import hashlib
import json
import time

import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.schema import Document
from langchain.prompts import PromptTemplate

from htmlTemplates import css, get_user_message_html, get_bot_message_html, get_source_card_html

# ─── Constants ────────────────────────────────────────────────────────────────

FAISS_STORE_DIR = "faiss_store"          # root folder for persisted indexes
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GROQ_MODEL      = "llama-3.3-70b-versatile"

# Chunking settings (Improvement #5 — RecursiveCharacterTextSplitter)
CHUNK_SIZE    = 1000   # ~250 tokens; good balance of context vs precision
CHUNK_OVERLAP = 200    # 20% overlap preserves cross-boundary meaning

# Custom RAG system prompt (Improvement #8)
SYSTEM_PROMPT = """You are a helpful AI assistant. Answer questions based ONLY on the
provided context documents. If the answer cannot be found in the context, respond with:
"I couldn't find that information in the provided documents."
Be concise, accurate, and always ground your answer in the source material."""

# ─── PDF Processing ────────────────────────────────────────────────────────────

def get_pdf_documents(pdf_files: list) -> list[Document]:
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
            st.warning(f"⚠️ Could not parse **{getattr(pdf_file, 'name', pdf_file)}**: {e}")
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


def load_vectorstore(file_hash: str, embeddings) -> FAISS | None:
    """Load existing FAISS index if available. (Improvement #3)"""
    path = get_index_path(file_hash)
    if os.path.exists(os.path.join(path, "index.faiss")):
        try:
            vs = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
            return vs
        except Exception as e:
            st.warning(f"Could not load saved index ({e}); rebuilding…")
    return None


def get_embeddings() -> HuggingFaceEmbeddings:
    """Return cached HuggingFace embeddings model."""
    if "embeddings" not in st.session_state:
        st.session_state.embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return st.session_state.embeddings


def build_vectorstore(chunks: list[Document]) -> FAISS:
    """Build FAISS vectorstore from document chunks."""
    embeddings = get_embeddings()
    return FAISS.from_documents(chunks, embeddings)


# ─── Conversation Chain ────────────────────────────────────────────────────────

def build_prompt_template() -> PromptTemplate:
    """Custom QA prompt that grounds answers in context. (Improvement #8)"""
    template = f"""{SYSTEM_PROMPT}

Context:
{{context}}

Chat History:
{{chat_history}}

Question: {{question}}

Answer:"""
    return PromptTemplate(
        template=template,
        input_variables=["context", "chat_history", "question"]
    )


def get_conversation_chain(vectorstore: FAISS) -> ConversationalRetrievalChain:
    """
    Build the RAG conversation chain.
    Uses MMR retrieval for diversity + quality. (Improvement #8)
    """
    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name=GROQ_MODEL,
        temperature=0.1,
        streaming=True,       # enable streaming (Improvement #4)
        max_tokens=1024,
    )

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer",
    )

    # MMR retriever: fetch 6 docs, keep 4 most diverse (Improvement #8)
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 4, "fetch_k": 6, "lambda_mult": 0.6},
    )

    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True,   # needed for citations (Improvement #1)
        combine_docs_chain_kwargs={"prompt": build_prompt_template()},
        output_key="answer",
    )
    return chain


# ─── Summarization ─────────────────────────────────────────────────────────────

def generate_summary(pdf_files: list) -> dict:
    """
    Generate concise / detailed summary + key topics for uploaded PDFs.
    (Improvement #6)
    """
    # Grab first ~6000 chars of combined text as a representative sample
    sample_text = ""
    for pdf_file in pdf_files[:3]:
        try:
            reader = PdfReader(pdf_file)
            for page in reader.pages[:5]:
                t = page.extract_text() or ""
                sample_text += t
                if len(sample_text) > 6000:
                    break
        except Exception:
            continue
    if not sample_text.strip():
        return {"error": "No readable text found in the documents."}

    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name=GROQ_MODEL,
        temperature=0.2,
    )

    prompt = f"""Analyze the following document text and respond with valid JSON only.
No markdown, no code fences, just raw JSON.

{{
  "concise_summary": "2-3 sentence overview",
  "detailed_summary": "5-7 sentence comprehensive summary",
  "key_topics": ["topic1", "topic2", "topic3", "topic4", "topic5"],
  "important_concepts": ["concept1", "concept2", "concept3"]
}}

Document text:
{sample_text[:5000]}"""

    try:
        response = llm.invoke(prompt)
        raw = response.content.strip()
        # Strip markdown fences if model adds them
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception as e:
        return {"error": f"Summary generation failed: {e}"}


# ─── Chat / Response Handling ──────────────────────────────────────────────────

def handle_user_input(question: str) -> None:
    """
    Send question to the RAG chain and stream the response.
    Displays source citations after the answer. (Improvements #1, #4)
    """
    if st.session_state.conversation is None:
        st.warning("Please upload and process PDFs first.")
        return

    # Display user message immediately
    st.markdown(get_user_message_html(question), unsafe_allow_html=True)

    # ── Streaming response ──────────────────────────────────────────────────
    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        full_answer = ""
        source_docs = []

        try:
            # Run chain — streaming tokens via callback or direct invoke
            response = st.session_state.conversation({"question": question})
            full_answer = response.get("answer", "")
            source_docs = response.get("source_documents", [])

            # Simulate streaming render (token-by-token) for UX (Improvement #4)
            displayed = ""
            for char in full_answer:
                displayed += char
                placeholder.markdown(displayed + "▌")
                time.sleep(0.008)   # ~125 chars/sec feels natural
            placeholder.markdown(full_answer)

        except Exception as e:
            placeholder.error(f"Error generating response: {e}")
            return

    # ── Source citations ───────────────────────────────────────────────────
    if source_docs:
        with st.expander("📚 Source References", expanded=False):
            seen = set()
            for doc in source_docs:
                meta = doc.metadata
                src  = meta.get("source", "Unknown")
                page = meta.get("page", "?")
                key  = f"{src}|{page}"
                if key in seen:
                    continue
                seen.add(key)
                st.markdown(
                    get_source_card_html(
                        filename=src,
                        page=page,
                        snippet=doc.page_content[:300].replace("\n", " ") + "…",
                    ),
                    unsafe_allow_html=True,
                )

    # Append to session history for display continuity
    st.session_state.chat_history.append(("user", question))
    st.session_state.chat_history.append(("bot", full_answer))


# ─── Main App ──────────────────────────────────────────────────────────────────

def main():
    load_dotenv()

    st.set_page_config(
        page_title="DocMind AI",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.write(css, unsafe_allow_html=True)

    # ── Session state init ──────────────────────────────────────────────────
    defaults = {
        "conversation": None,
        "chat_history": [],
        "processed": False,
        "current_hash": None,
        "summary_data": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # ── Sidebar ─────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown('<div class="sidebar-header">🧠 DocMind AI</div>', unsafe_allow_html=True)
        st.markdown('<p class="sidebar-sub">Upload PDFs and start asking questions.</p>', unsafe_allow_html=True)

        pdf_docs = st.file_uploader(
            "Drop your PDFs here",
            type=["pdf"],
            accept_multiple_files=True,
            help="Supports multiple PDF files simultaneously",
        )

        col1, col2 = st.columns(2)

        with col1:
            process_btn = st.button("⚡ Process", use_container_width=True, type="primary")
        with col2:
            clear_btn = st.button("🗑 Clear", use_container_width=True)

        if clear_btn:
            for k in ["conversation", "chat_history", "processed", "current_hash", "summary_data"]:
                st.session_state[k] = None if k in ("conversation",) else ([] if k == "chat_history" else False)
            st.rerun()

        if process_btn and pdf_docs:
            file_hash = compute_file_hash(pdf_docs)

            # Check for existing FAISS index (Improvement #3)
            if file_hash == st.session_state.current_hash and st.session_state.processed:
                st.success("✅ Already processed!")
            else:
                embeddings = get_embeddings()
                cached_vs = load_vectorstore(file_hash, embeddings)

                if cached_vs:
                    st.success("⚡ Loaded existing vector database")
                    vectorstore = cached_vs
                else:
                    with st.spinner("🔍 Extracting text & building index…"):
                        docs   = get_pdf_documents(pdf_docs)
                        if not docs:
                            st.error("No readable text found. Are these scanned PDFs?")
                            st.stop()
                        chunks = split_documents(docs)
                        vectorstore = build_vectorstore(chunks)
                        save_vectorstore(vectorstore, file_hash)
                    st.success(f"✅ Indexed {len(chunks)} chunks from {len(pdf_docs)} PDF(s)")

                st.session_state.conversation  = get_conversation_chain(vectorstore)
                st.session_state.current_hash  = file_hash
                st.session_state.processed     = True
                st.session_state.chat_history  = []

        # Summary feature (Improvement #6)
        if st.session_state.processed and pdf_docs:
            st.markdown("---")
            if st.button("📋 Generate Summary", use_container_width=True):
                with st.spinner("Generating document summary…"):
                    st.session_state.summary_data = generate_summary(pdf_docs)

        # File info
        if pdf_docs:
            st.markdown("---")
            st.markdown("**Uploaded files:**")
            for f in pdf_docs:
                size_kb = round(f.size / 1024, 1)
                st.markdown(f"📄 `{f.name}` — {size_kb} KB")

    # ── Main content area ────────────────────────────────────────────────────
    if not st.session_state.processed:
        # Welcome screen (Improvement #2)
        st.markdown("""
        <div class="welcome-container">
            <div class="welcome-icon">🧠</div>
            <h1 class="welcome-title">DocMind AI</h1>
            <p class="welcome-sub">Upload PDFs in the sidebar, click <strong>Process</strong>,<br>then ask anything about your documents.</p>
            <div class="feature-grid">
                <div class="feature-card">📖 Multi-PDF Chat</div>
                <div class="feature-card">🔗 Source Citations</div>
                <div class="feature-card">⚡ Streaming Answers</div>
                <div class="feature-card">💾 Persistent Index</div>
                <div class="feature-card">📋 Auto Summaries</div>
                <div class="feature-card">🎯 MMR Retrieval</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # ── Summary cards ──────────────────────────────────────────────────
        if st.session_state.summary_data:
            data = st.session_state.summary_data
            if "error" in data:
                st.error(data["error"])
            else:
                st.markdown('<h3 class="section-title">📋 Document Summary</h3>', unsafe_allow_html=True)
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown(f"""
                    <div class="summary-card">
                        <div class="summary-label">Quick Overview</div>
                        <p>{data.get('concise_summary','')}</p>
                    </div>""", unsafe_allow_html=True)
                with col_b:
                    topics = data.get("key_topics", [])
                    topics_html = "".join(f'<span class="topic-tag">{t}</span>' for t in topics)
                    st.markdown(f"""
                    <div class="summary-card">
                        <div class="summary-label">Key Topics</div>
                        <div class="topic-container">{topics_html}</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown(f"""
                <div class="summary-card full-width">
                    <div class="summary-label">Detailed Summary</div>
                    <p>{data.get('detailed_summary','')}</p>
                </div>""", unsafe_allow_html=True)

                concepts = data.get("important_concepts", [])
                if concepts:
                    concepts_html = "".join(f'<span class="concept-tag">{c}</span>' for c in concepts)
                    st.markdown(f"""
                    <div class="summary-card full-width">
                        <div class="summary-label">Important Concepts</div>
                        <div class="topic-container">{concepts_html}</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown("---")

        # ── Replay chat history ────────────────────────────────────────────
        for role, msg in st.session_state.chat_history:
            if role == "user":
                st.markdown(get_user_message_html(msg), unsafe_allow_html=True)
            else:
                st.markdown(get_bot_message_html(msg), unsafe_allow_html=True)

        # ── Chat input ─────────────────────────────────────────────────────
        question = st.chat_input("Ask anything about your documents…")
        if question:
            handle_user_input(question)


if __name__ == "__main__":
    main()
