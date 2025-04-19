from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from backend.db.database import get_db
from backend.schemas.highlights import HighlightCreate, HighlightResponse, SmartHighlightRequest, SmartHighlightResponse
from backend.services.highlight_service import HighlightService
from backend.services.document_service import DocumentService

router = APIRouter(prefix="/highlights", tags=["highlights"])

highlight_service = HighlightService()
document_service = DocumentService()

@router.post("/", response_model=HighlightResponse, status_code=status.HTTP_201_CREATED)
async def create_highlight(
    highlight: HighlightCreate,
    session_id: str = Query(..., description="Unique session ID"),
    db: Session = Depends(get_db)
):
    """Create a new highlight."""
    # Check if document exists
    document = document_service.get_document(db, highlight.document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {highlight.document_id} not found"
        )

    # No authorization check since we removed authentication

    # Create highlight
    try:
        # Use a default user ID since we removed authentication
        user_id = 1

        db_highlight = highlight_service.create_highlight(
            db=db,
            text=highlight.text,
            document_id=highlight.document_id,
            user_id=user_id,
            highlight_type=highlight.highlight_type,
            sentence_type=highlight.sentence_type,
            note=highlight.note
        )
        return db_highlight
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating highlight: {str(e)}"
        )

@router.post("/smart", response_model=SmartHighlightResponse)
async def get_smart_highlight(
    request: SmartHighlightRequest,
    session_id: str = Query(..., description="Unique session ID")
):
    """Generate a smart highlight."""
    try:
        result = highlight_service.get_smart_highlight(request.text)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating smart highlight: {str(e)}"
        )

@router.get("/", response_model=List[HighlightResponse])
async def get_user_highlights(
    session_id: str = Query(..., description="Unique session ID"),
    db: Session = Depends(get_db)
):
    """Get all highlights."""
    # Use a default user ID since we removed authentication
    user_id = 1
    return highlight_service.get_user_highlights(db, user_id)

@router.get("/document/{document_id}", response_model=List[HighlightResponse])
async def get_document_highlights(
    document_id: str,
    session_id: str = Query(..., description="Unique session ID"),
    db: Session = Depends(get_db)
):
    """Get all highlights for a document."""
    # Check if document exists
    document = document_service.get_document(db, document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )

    # No authorization check since we removed authentication

    # Use a default user ID since we removed authentication
    user_id = 1
    return highlight_service.get_document_highlights(db, document_id, user_id)

@router.delete("/{highlight_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_highlight(
    highlight_id: int,
    session_id: str = Query(..., description="Unique session ID"),
    db: Session = Depends(get_db)
):
    """Delete a highlight."""
    # Use a default user ID since we removed authentication
    user_id = 1
    result = highlight_service.delete_highlight(db, highlight_id, user_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Highlight with ID {highlight_id} not found"
        )
