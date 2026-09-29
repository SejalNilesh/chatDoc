"""
DocMind AI retrieval and LLM logic.

The functions here contain the original RAG conversation-chain and
document-summary logic moved out of the Streamlit UI layer.
"""

import json
import os

from PyPDF2 import PdfReader
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain_groq import ChatGroq
from langchain_community.vectorstores import FAISS

from .config import GROQ_MODEL, SYSTEM_PROMPT


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
