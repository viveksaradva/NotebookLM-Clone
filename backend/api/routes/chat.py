from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.schemas.chat import ChatRequest, ChatResponse
from backend.services.chat_service import ChatService
from backend.services.document_service import DocumentService

router = APIRouter(prefix="/chat", tags=["chat"])

chat_service = ChatService()
document_service = DocumentService()

@router.post("/query", response_model=ChatResponse)
async def query_document(
    request: ChatRequest,
    session_id: str = Query(None, description="Unique session ID"),
    db: Session = Depends(get_db)
):
    """Query a document and get a response."""
    # Check if document exists
    document = document_service.get_document(db, request.document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {request.document_id} not found"
        )

    # No authorization check since we removed authentication

    # Process query
    try:
        # Use the session_id from the query parameter if not provided in the request
        if not request.session_id and session_id:
            request.session_id = session_id

        result = chat_service.process_query(
            query=request.query,
            document_id=request.document_id,
            session_id=request.session_id
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )

@router.post("/create-session", response_model=dict)
async def create_chat_session(
    document_id: str,
    session_id: str = Query(..., description="Unique session ID"),
    db: Session = Depends(get_db)
):
    """Create a new chat session."""
    # Check if document exists
    document = document_service.get_document(db, document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )

    # No authorization check since we removed authentication

    # Create session
    try:
        result = chat_service.create_session(document_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating chat session: {str(e)}"
        )

@router.post("/reset-session", response_model=dict)
async def reset_chat_session(
    session_id: str,
    user_session_id: str = Query(..., description="Unique user session ID")
):
    """Reset a chat session."""
    try:
        result = chat_service.reset_session(session_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resetting chat session: {str(e)}"
        )
