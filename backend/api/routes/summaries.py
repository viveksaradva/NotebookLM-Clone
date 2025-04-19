from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.schemas.summaries import SummaryRequest, SummaryResponse, SemanticSummaryRequest, SemanticSummaryResponse
from backend.services.summary_service import SummaryService
from backend.services.document_service import DocumentService

router = APIRouter(prefix="/summaries", tags=["summaries"])

summary_service = SummaryService()
document_service = DocumentService()

@router.post("/document", response_model=SummaryResponse)
async def generate_document_summary(
    request: SummaryRequest,
    session_id: str = Query(..., description="Unique session ID"),
    db: Session = Depends(get_db)
):
    """Generate a summary for a document."""
    # Check if document exists
    document = document_service.get_document(db, request.document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {request.document_id} not found"
        )

    # No authorization check since we removed authentication

    # Generate summary
    try:
        result = summary_service.generate_document_summary(
            document_id=request.document_id,
            max_length=request.max_length
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating summary: {str(e)}"
        )

@router.post("/semantic", response_model=SemanticSummaryResponse)
async def generate_semantic_summary(
    request: SemanticSummaryRequest,
    session_id: str = Query(..., description="Unique session ID")
):
    """Generate a semantic summary from highlights."""
    try:
        result = summary_service.generate_semantic_summary(request.highlights)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating semantic summary: {str(e)}"
        )
