"""Application-specific exceptions."""


class DocumentIndexNotFoundError(Exception):
    """Raised when a query targets an index that has not been ingested."""


class InvalidDocumentError(Exception):
    """Raised when uploaded documents cannot be processed."""


class LLMServiceError(Exception):
    """Raised when the language-model operation fails."""
