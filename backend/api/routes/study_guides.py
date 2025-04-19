from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.schemas.study_guides import StudyGuideRequest, StudyGuideResponse
from backend.services.study_guide_service import StudyGuideService
from backend.services.document_service import DocumentService

router = APIRouter(prefix="/study-guides", tags=["study-guides"])

study_guide_service = StudyGuideService()
document_service = DocumentService()

@router.post("/generate", response_model=StudyGuideResponse)
async def generate_study_guide(
    request: StudyGuideRequest,
    session_id: str = Query(..., description="Unique session ID"),
    db: Session = Depends(get_db)
):
    """Generate a study guide for a document."""
    # Check if document exists
    document = document_service.get_document(db, request.document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {request.document_id} not found"
        )

    # No authorization check since we removed authentication

    # Generate study guide
    try:
        result = study_guide_service.generate_study_guide(
            document_id=request.document_id,
            format=request.format
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating study guide: {str(e)}"
        )
