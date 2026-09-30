"""Document ingestion and summary endpoints."""

from io import BytesIO
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.core.dependencies import get_ingestion_service, get_summary_service
from app.core.exceptions import InvalidDocumentError, LLMServiceError
from app.schemas.document import IngestResponse, SummaryResponse
from app.services.ingestion_service import IngestionService
from app.services.summary_service import SummaryService

router = APIRouter(prefix="/documents", tags=["documents"])


async def _upload_files_to_file_objects(
    files: list[UploadFile],
) -> list[BytesIO]:
    """Convert FastAPI uploads to file-like objects used by the RAG services."""
    file_objects: list[BytesIO] = []

    for upload in files:
        content = await upload.read()
        pdf = BytesIO(content)
        pdf.name = upload.filename or "uploaded.pdf"
        pdf.size = len(content)
        file_objects.append(pdf)

    return file_objects


@router.post("/ingest", response_model=IngestResponse)
async def ingest_documents(
    files: Annotated[list[UploadFile], File(...)],
    service: IngestionService = Depends(get_ingestion_service),
) -> IngestResponse:
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload at least one PDF.",
        )

    try:
        pdf_files = await _upload_files_to_file_objects(files)
        return IngestResponse(**service.ingest(pdf_files))
    except InvalidDocumentError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/summary",
    response_model=SummaryResponse,
    response_model_exclude_none=True,
)
async def summarize_documents(
    files: Annotated[list[UploadFile], File(...)],
    service: SummaryService = Depends(get_summary_service),
) -> SummaryResponse:
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload at least one PDF.",
        )

    try:
        pdf_files = await _upload_files_to_file_objects(files)
        return SummaryResponse(**service.generate(pdf_files))
    except LLMServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Invalid summary response: {exc}",
        ) from exc
