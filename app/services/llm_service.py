"""Groq LLM provider service."""

from langchain_groq import ChatGroq

from app.core.config import Settings
from app.core.exceptions import LLMServiceError


class LLMService:
    """Keep provider-specific model setup out of the use-case services."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._chat_model: ChatGroq | None = None
        self._summary_model: ChatGroq | None = None

    def _ensure_api_key(self) -> None:
        if not self.settings.GROQ_API_KEY:
            raise LLMServiceError("GROQ_API_KEY is not configured.")

    def get_chat_model(self) -> ChatGroq:
        self._ensure_api_key()
        if self._chat_model is None:
            self._chat_model = ChatGroq(
                groq_api_key=self.settings.GROQ_API_KEY,
                model_name=self.settings.GROQ_MODEL,
                temperature=0.1,
                streaming=True,
                max_tokens=1024,
            )
        return self._chat_model

    def get_summary_model(self) -> ChatGroq:
        self._ensure_api_key()
        if self._summary_model is None:
            self._summary_model = ChatGroq(
                groq_api_key=self.settings.GROQ_API_KEY,
                model_name=self.settings.GROQ_MODEL,
                temperature=0.2,
            )
        return self._summary_model

    def invoke_summary(self, prompt: str):
        try:
            return self.get_summary_model().invoke(prompt)
        except LLMServiceError:
            raise
        except Exception as exc:
            raise LLMServiceError(f"Summary generation failed: {exc}") from exc
