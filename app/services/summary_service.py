"""Document summarization use case."""

import json

from PyPDF2 import PdfReader

from app.core.config import Settings
from app.services.llm_service import LLMService


class SummaryService:
    """Generate a structured summary from a representative PDF sample."""

    def __init__(self, settings: Settings, llm_service: LLMService) -> None:
        self.settings = settings
        self.llm_service = llm_service

    @staticmethod
    def _extract_sample(pdf_files: list) -> str:
        sample_text = ""
        for pdf_file in pdf_files[:3]:
            try:
                pdf_file.seek(0)
                reader = PdfReader(pdf_file)
                for page in reader.pages[:5]:
                    sample_text += page.extract_text() or ""
                    if len(sample_text) > 6000:
                        return sample_text
            except Exception:
                continue
        return sample_text

    @staticmethod
    def _parse_response(raw: str) -> dict:
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```", 2)[1]
            if raw.lstrip().startswith("json"):
                raw = raw.lstrip()[4:]
        return json.loads(raw.strip())

    def generate(self, pdf_files: list) -> dict:
        sample_text = self._extract_sample(pdf_files)
        if not sample_text.strip():
            return {"error": "No readable text found in the documents."}

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

        response = self.llm_service.invoke_summary(prompt)
        return self._parse_response(response.content)
