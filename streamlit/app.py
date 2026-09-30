"""DocMind AI Streamlit frontend.

This module contains presentation and user-interaction logic only.
All document processing, retrieval, embeddings, FAISS persistence, and LLM
operations are performed by the FastAPI backend through ``api_client.py``.
"""

from __future__ import annotations

import html
import os
import time
from typing import Any

import streamlit as st
from dotenv import load_dotenv

from api_client import DocMindAPIClient, APIClientError
from htmlTemplates import (
    css,
    get_bot_message_html,
    get_source_card_html,
    get_user_message_html,
    get_welcome_html,
)


load_dotenv()

API_BASE_URL = os.getenv("DOCMIND_API_URL", "http://localhost:8000").rstrip("/")
API_TIMEOUT = int(os.getenv("DOCMIND_API_TIMEOUT", "300"))
api_client = DocMindAPIClient(API_BASE_URL, timeout=API_TIMEOUT)


# -----------------------------------------------------------------------------
# Session state
# -----------------------------------------------------------------------------

def initialize_session_state() -> None:
    defaults = {
        "chat_history": [],
        "processed": False,
        "current_hash": None,
        "summary_data": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_session() -> None:
    st.session_state.chat_history = []
    st.session_state.processed = False
    st.session_state.current_hash = None
    st.session_state.summary_data = None


# -----------------------------------------------------------------------------
# API helpers
# -----------------------------------------------------------------------------

def _uploaded_files_payload(pdf_docs: list[Any]) -> list[tuple[str, bytes, str]]:
    return [
        (pdf.name, pdf.getvalue(), "application/pdf")
        for pdf in pdf_docs
    ]


def _friendly_api_error(exc: Exception) -> str:
    if isinstance(exc, APIClientError):
        return str(exc)
    return f"Unexpected error: {exc}"


# -----------------------------------------------------------------------------
# Document actions
# -----------------------------------------------------------------------------

def process_documents(pdf_docs: list[Any]) -> None:
    try:
        response = api_client.ingest(_uploaded_files_payload(pdf_docs))
    except Exception as exc:
        st.error(_friendly_api_error(exc))
        return

    st.session_state.current_hash = response["file_hash"]
    st.session_state.processed = True
    st.session_state.chat_history = []
    st.session_state.summary_data = None

    if response.get("status") == "loaded_existing":
        st.success("Loaded existing vector index.")
    else:
        indexed_chunks = response.get("indexed_chunks", 0)
        st.success(
            f"Indexed {indexed_chunks} chunks across {len(pdf_docs)} file(s)."
        )


def generate_summary(pdf_docs: list[Any]) -> None:
    try:
        st.session_state.summary_data = api_client.summary(
            _uploaded_files_payload(pdf_docs)
        )
    except Exception as exc:
        st.session_state.summary_data = {"error": _friendly_api_error(exc)}


# -----------------------------------------------------------------------------
# Chat
# -----------------------------------------------------------------------------

def handle_user_input(question: str) -> None:
    question = question.strip()
    if not question:
        return

    if not st.session_state.processed or not st.session_state.current_hash:
        st.warning("Please upload and process PDFs first.")
        return

    st.markdown(get_user_message_html(question), unsafe_allow_html=True)

    try:
        response = api_client.query(
            file_hash=st.session_state.current_hash,
            question=question,
        )
    except Exception as exc:
        st.error(f"Error generating response: {_friendly_api_error(exc)}")
        return

    full_answer = response.get("answer", "")

    with st.chat_message("assistant"):
        placeholder = st.empty()
        displayed = ""
        for char in full_answer:
            displayed += char
            placeholder.markdown(displayed + "▌")
            time.sleep(0.008)
        placeholder.markdown(full_answer)

    sources = response.get("sources", [])
    if sources:
        with st.expander("Source References", expanded=False):
            for source in sources:
                st.markdown(
                    get_source_card_html(
                        filename=source.get("document", "Unknown"),
                        page=source.get("page", "?"),
                        snippet=source.get("snippet", ""),
                    ),
                    unsafe_allow_html=True,
                )

    st.session_state.chat_history.append(("user", question))
    st.session_state.chat_history.append(("bot", full_answer))


# -----------------------------------------------------------------------------
# Rendering
# -----------------------------------------------------------------------------

def render_sidebar() -> list[Any] | None:
    with st.sidebar:
        st.markdown(
            '<div class="sidebar-wordmark">Doc<span>Mind</span></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<span class="sidebar-tagline">Chat with your documents</span>',
            unsafe_allow_html=True,
        )

        pdf_docs = st.file_uploader(
            "Drop your PDFs here",
            type=["pdf"],
            accept_multiple_files=True,
            help="Supports multiple PDF files simultaneously",
        )

        col1, col2 = st.columns(2)

        with col1:
            process_btn = st.button(
                "Process",
                use_container_width=True,
                type="primary",
            )

        with col2:
            clear_btn = st.button("Clear", use_container_width=True)

        if clear_btn:
            clear_session()
            st.rerun()

        if process_btn:
            if not pdf_docs:
                st.warning("Please upload at least one PDF.")
            else:
                with st.spinner("Processing documents..."):
                    process_documents(pdf_docs)

        if st.session_state.processed and pdf_docs:
            st.markdown("---")
            if st.button("Generate Summary", use_container_width=True):
                with st.spinner("Generating document summary..."):
                    generate_summary(pdf_docs)

        if pdf_docs:
            st.markdown(
                '<div class="sidebar-divider"></div>'
                '<span class="sidebar-section-label">Uploaded files</span>',
                unsafe_allow_html=True,
            )

            for file in pdf_docs:
                size_kb = round(file.size / 1024, 1)
                safe_name = html.escape(file.name)
                st.markdown(
                    f'<div class="file-pill">'
                    f'<span class="file-pill-icon">'
                    f'<svg viewBox="0 0 12 14" xmlns="http://www.w3.org/2000/svg">'
                    f'<path d="M1 1h7l3 3v9H1V1z"/></svg></span>'
                    f'{safe_name} &nbsp;'
                    f'<span style="color:var(--text-muted);font-size:0.72rem">'
                    f'{size_kb} KB</span></div>',
                    unsafe_allow_html=True,
                )

    return pdf_docs


def render_summary() -> None:
    data = st.session_state.summary_data
    if not data:
        return

    error_message = data.get("error")
    if error_message:
        st.error(str(error_message))
        return

    st.markdown(
        '<div class="section-heading">Document Summary</div>',
        unsafe_allow_html=True,
    )

    col_a, col_b = st.columns(2)

    with col_a:
        concise = html.escape(data.get("concise_summary", ""))
        st.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-card-label">Quick Overview</div>
                <p>{concise}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_b:
        topics = data.get("key_topics", [])
        topics_html = "".join(
            f'<span class="tag tag-topic">{html.escape(str(topic))}</span>'
            for topic in topics
        )
        st.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-card-label">Key Topics</div>
                <div class="tag-row">{topics_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    detailed = html.escape(data.get("detailed_summary", ""))
    st.markdown(
        f"""
        <div class="summary-card full-width">
            <div class="summary-card-label">Detailed Summary</div>
            <p>{detailed}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    concepts = data.get("important_concepts", [])
    if concepts:
        concepts_html = "".join(
            f'<span class="tag tag-concept">{html.escape(str(concept))}</span>'
            for concept in concepts
        )
        st.markdown(
            f"""
            <div class="summary-card full-width">
                <div class="summary-card-label">Important Concepts</div>
                <div class="tag-row">{concepts_html}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")


def render_chat() -> None:
    for role, message in st.session_state.chat_history:
        if role == "user":
            st.markdown(get_user_message_html(message), unsafe_allow_html=True)
        else:
            st.markdown(get_bot_message_html(message), unsafe_allow_html=True)

    question = st.chat_input("Ask anything about your documents...")
    if question:
        handle_user_input(question)


def main() -> None:
    st.set_page_config(
        page_title="DocMind AI",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.write(css, unsafe_allow_html=True)
    initialize_session_state()

    pdf_docs = render_sidebar()

    if not st.session_state.processed:
        st.markdown(get_welcome_html(), unsafe_allow_html=True)
        return

    render_summary()
    render_chat()


if __name__ == "__main__":
    main()
