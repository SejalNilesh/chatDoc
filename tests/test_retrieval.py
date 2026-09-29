"""
Tests for the DocMind retrieval/LLM layer.

No real Groq request is made. The test verifies that the existing retrieval
settings are wired into the LangChain conversation chain.
"""

from types import SimpleNamespace

from app import retrieval


def test_build_prompt_template_contains_grounding_instructions():
    prompt = retrieval.build_prompt_template()

    prompt_text = prompt.template

    assert "provided context documents" in prompt_text
    assert "Context:" in prompt_text
    assert "Chat History:" in prompt_text
    assert "Question:" in prompt_text
    assert "Answer:" in prompt_text


def test_get_conversation_chain_uses_mmr_and_returns_sources(monkeypatch):
    """The existing MMR settings and source-document behavior are preserved."""

    captured = {}

    fake_vectorstore = SimpleNamespace()

    def fake_as_retriever(**kwargs):
        captured["retriever_kwargs"] = kwargs
        return "fake-retriever"

    fake_vectorstore.as_retriever = fake_as_retriever

    class FakeChatGroq:
        def __init__(self, **kwargs):
            captured["llm_kwargs"] = kwargs

    class FakeMemory:
        def __init__(self, **kwargs):
            captured["memory_kwargs"] = kwargs

    class FakeChainFactory:
        @classmethod
        def from_llm(cls, **kwargs):
            captured["chain_kwargs"] = kwargs
            return "fake-chain"

    monkeypatch.setattr(retrieval, "ChatGroq", FakeChatGroq)
    monkeypatch.setattr(retrieval, "ConversationBufferMemory", FakeMemory)
    monkeypatch.setattr(retrieval, "ConversationalRetrievalChain", FakeChainFactory)

    chain = retrieval.get_conversation_chain(fake_vectorstore)

    assert chain == "fake-chain"

    assert captured["retriever_kwargs"] == {
        "search_type": "mmr",
        "search_kwargs": {"k": 4, "fetch_k": 6, "lambda_mult": 0.6},
    }

    assert captured["llm_kwargs"]["temperature"] == 0.1
    assert captured["llm_kwargs"]["streaming"] is True
    assert captured["llm_kwargs"]["max_tokens"] == 1024

    assert captured["chain_kwargs"]["retriever"] == "fake-retriever"
    assert captured["chain_kwargs"]["return_source_documents"] is True


def test_generate_summary_parses_json_response(monkeypatch):
    """The summary helper returns structured JSON produced by the LLM."""

    class FakePage:
        def extract_text(self):
            return "Document text about machine learning and retrieval."

    class FakeReader:
        def __init__(self, _file):
            self.pages = [FakePage()]

    class FakeLLM:
        def invoke(self, _prompt):
            return SimpleNamespace(
                content='{"concise_summary":"Summary","detailed_summary":"Details",'
                        '"key_topics":["RAG"],"important_concepts":["retrieval"]}'
            )

    monkeypatch.setattr(retrieval, "PdfReader", FakeReader)
    monkeypatch.setattr(retrieval, "ChatGroq", lambda **_: FakeLLM())

    pdf_file = SimpleNamespace(name="sample.pdf")
    result = retrieval.generate_summary([pdf_file])

    assert result["concise_summary"] == "Summary"
    assert result["key_topics"] == ["RAG"]
    assert result["important_concepts"] == ["retrieval"]
