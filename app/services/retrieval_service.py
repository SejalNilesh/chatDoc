"""Conversational RAG query service."""

from pathlib import Path

from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS

from app.core.config import Settings
from app.core.exceptions import DocumentIndexNotFoundError
from app.schemas.document import Source
from app.services.embedding_service import EmbeddingService
from app.services.llm_service import LLMService


class RetrievalService:
    """Load FAISS indexes, retrieve context, and generate grounded answers."""

    def __init__(
        self,
        settings: Settings,
        embedding_service: EmbeddingService,
        llm_service: LLMService,
    ) -> None:
        self.settings = settings
        self.embedding_service = embedding_service
        self.llm_service = llm_service
        self._conversation_cache: dict[str, ConversationalRetrievalChain] = {}

    def _index_path(self, file_hash: str) -> Path:
        return self.settings.FAISS_STORE_DIR / file_hash

    def _load_vectorstore(self, file_hash: str) -> FAISS:
        path = self._index_path(file_hash)
        if not (path / "index.faiss").exists():
            raise DocumentIndexNotFoundError(
                "No indexed document set found for this file_hash. Ingest PDFs first."
            )

        return FAISS.load_local(
            str(path),
            self.embedding_service.get_embeddings(),
            allow_dangerous_deserialization=True,
        )

    def _build_prompt(self) -> PromptTemplate:
        template = f"""{self.settings.SYSTEM_PROMPT}

Context:
{{context}}

Chat History:
{{chat_history}}

Question: {{question}}

Answer:"""
        return PromptTemplate(
            template=template,
            input_variables=["context", "chat_history", "question"],
        )

    def _create_chain(self, vectorstore: FAISS) -> ConversationalRetrievalChain:
        retriever = vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 4, "fetch_k": 6, "lambda_mult": 0.6},
        )
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer",
        )

        return ConversationalRetrievalChain.from_llm(
            llm=self.llm_service.get_chat_model(),
            retriever=retriever,
            memory=memory,
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": self._build_prompt()},
            output_key="answer",
        )

    def _get_conversation(self, file_hash: str):
        if file_hash not in self._conversation_cache:
            vectorstore = self._load_vectorstore(file_hash)
            self._conversation_cache[file_hash] = self._create_chain(vectorstore)
        return self._conversation_cache[file_hash]

    @staticmethod
    def _extract_sources(source_documents) -> list[Source]:
        sources: list[Source] = []
        seen: set[str] = set()

        for document in source_documents:
            metadata = document.metadata or {}
            source = metadata.get("source", "Unknown")
            page = metadata.get("page", "?")
            key = f"{source}|{page}"
            if key in seen:
                continue

            seen.add(key)
            sources.append(
                Source(
                    document=source,
                    page=page,
                    snippet=document.page_content[:300].replace("\n", " ") + "…",
                )
            )

        return sources

    def ask(self, file_hash: str, query: str) -> dict:
        conversation = self._get_conversation(file_hash)
        response = conversation.invoke({"question": query})

        return {
            "answer": response.get("answer", ""),
            "sources": self._extract_sources(
                response.get("source_documents", [])
            ),
        }
