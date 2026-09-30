"""Document question-answering endpoint."""

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_retrieval_service
from app.core.exceptions import DocumentIndexNotFoundError, LLMServiceError
from app.schemas.query import QueryRequest
from app.schemas.response import QueryResponse
from app.services.retrieval_service import RetrievalService

router = APIRouter(prefix="/query", tags=["query"])


@router.post("", response_model=QueryResponse)
def query_documents(
    request: QueryRequest,
    service: RetrievalService = Depends(get_retrieval_service),
) -> QueryResponse:
    try:
        result = service.ask(request.file_hash, request.query)
        return QueryResponse(**result)
    except DocumentIndexNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except LLMServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating response: {exc}",
        ) from exc
