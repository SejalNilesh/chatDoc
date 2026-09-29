"""
DocMind AI — Streamlit UI.

The Streamlit layer is intentionally responsible only for presentation,
user interaction, and calling the DocMind API. PDF ingestion, retrieval,
embeddings, FAISS persistence, and LLM logic live behind the API.
"""

import os
import time

import requests
import streamlit as st
from dotenv import load_dotenv

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


def _api_post(path: str, **kwargs):
    """Send a POST request to the DocMind API and return the JSON body."""
    url = f"{API_BASE_URL}{path}"
    try:
        response = requests.post(url, timeout=API_TIMEOUT, **kwargs)
    except requests.RequestException as e:
        raise RuntimeError(
            f"Could not connect to the DocMind API at {API_BASE_URL}. "
            f"Start the API server first. Details: {e}"
        ) from e

    try:
        payload = response.json()
    except ValueError:
        payload = {"detail": response.text or "Invalid API response."}

    if not response.ok:
        detail = payload.get("detail", "API request failed.")
        raise RuntimeError(str(detail))

    return payload


def _uploaded_files_payload(pdf_docs):
    """Build a multipart payload from Streamlit UploadedFile objects."""
    return [
        (
            "files",
            (
                pdf.name,
                pdf.getvalue(),
                "application/pdf",
            ),
        )
        for pdf in pdf_docs
    ]


def process_documents(pdf_docs) -> None:
    """Send uploaded PDFs to the ingestion API and update UI state."""
    try:
        response = _api_post(
            "/ingest",
            files=_uploaded_files_payload(pdf_docs),
        )
    except RuntimeError as e:
        st.error(str(e))
        return

    st.session_state.current_hash = response["file_hash"]
    st.session_state.processed = True
    st.session_state.chat_history = []

    if response.get("status") == "loaded_existing":
        st.success("Loaded existing vector index.")
    else:
        indexed_chunks = response.get("indexed_chunks", 0)
        st.success(
            f"Indexed {indexed_chunks} chunks across {len(pdf_docs)} file(s)."
        )


def handle_user_input(question: str) -> None:
    """
    Send the question to the retrieval API and render the answer + sources.
    """
    if not st.session_state.processed or not st.session_state.current_hash:
        st.warning("Please upload and process PDFs first.")
        return

    st.markdown(get_user_message_html(question), unsafe_allow_html=True)

    with st.chat_message("assistant"):
        placeholder = st.empty()

        try:
            response = _api_post(
                "/query",
                json={
                    "file_hash": st.session_state.current_hash,
                    "query": question,
                },
            )
        except RuntimeError as e:
            placeholder.error(f"Error generating response: {e}")
            return

        full_answer = response.get("answer", "")

        # Preserve the existing UX: display the completed answer character-by-character.
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

    # Keep the existing display history behavior.
    st.session_state.chat_history.append(("user", question))
    st.session_state.chat_history.append(("bot", full_answer))


def generate_summary(pdf_docs) -> None:
    """Request the existing summary feature through the API."""
    try:
        st.session_state.summary_data = _api_post(
            "/summary",
            files=_uploaded_files_payload(pdf_docs),
        )
    except RuntimeError as e:
        st.session_state.summary_data = {"error": str(e)}


def clear_session() -> None:
    """Reset the Streamlit UI state."""
    for key in [
        "conversation",
        "chat_history",
        "processed",
        "current_hash",
        "summary_data",
    ]:
        st.session_state[key] = (
            None
            if key in ("conversation", "current_hash")
            else ([] if key == "chat_history" else False)
        )


def main():
    st.set_page_config(
        page_title="DocMind AI",
        page_icon="doc",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.write(css, unsafe_allow_html=True)

    defaults = {
        "conversation": None,
        "chat_history": [],
        "processed": False,
        "current_hash": None,
        "summary_data": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

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

        if process_btn and pdf_docs:
            process_documents(pdf_docs)

        # Summary feature remains in the UI; generation itself is now handled by the API.
        if st.session_state.processed and pdf_docs:
            st.markdown("---")
            if st.button("Generate Summary", use_container_width=True):
                with st.spinner("Generating document summary…"):
                    generate_summary(pdf_docs)

        if pdf_docs:
            st.markdown(
                '<div class="sidebar-divider"></div>'
                '<span class="sidebar-section-label">Uploaded files</span>',
                unsafe_allow_html=True,
            )
            for file in pdf_docs:
                size_kb = round(file.size / 1024, 1)
                st.markdown(
                    f'<div class="file-pill">'
                    f'<span class="file-pill-icon">'
                    f'<svg viewBox="0 0 12 14" xmlns="http://www.w3.org/2000/svg">'
                    f'<path d="M1 1h7l3 3v9H1V1z"/></svg></span>'
                    f'{file.name} &nbsp;'
                    f'<span style="color:var(--text-muted);font-size:0.72rem">'
                    f'{size_kb} KB</span></div>',
                    unsafe_allow_html=True,
                )

    if not st.session_state.processed:
        st.markdown(get_welcome_html(), unsafe_allow_html=True)
    else:
        if st.session_state.summary_data:
            data = st.session_state.summary_data
            if "error" in data:
                st.error(data["error"])
            else:
                st.markdown(
                    '<div class="section-heading">Document Summary</div>',
                    unsafe_allow_html=True,
                )
                col_a, col_b = st.columns(2)

                with col_a:
                    st.markdown(
                        f"""
                        <div class="summary-card">
                            <div class="summary-card-label">Quick Overview</div>
                            <p>{data.get('concise_summary', '')}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with col_b:
                    topics = data.get("key_topics", [])
                    topics_html = "".join(
                        f'<span class="tag tag-topic">{topic}</span>'
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

                st.markdown(
                    f"""
                    <div class="summary-card full-width">
                        <div class="summary-card-label">Detailed Summary</div>
                        <p>{data.get('detailed_summary', '')}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                concepts = data.get("important_concepts", [])
                if concepts:
                    concepts_html = "".join(
                        f'<span class="tag tag-concept">{concept}</span>'
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

        for role, message in st.session_state.chat_history:
            if role == "user":
                st.markdown(get_user_message_html(message), unsafe_allow_html=True)
            else:
                st.markdown(get_bot_message_html(message), unsafe_allow_html=True)

        question = st.chat_input("Ask anything about your documents…")
        if question:
            handle_user_input(question)


if __name__ == "__main__":
    main()
