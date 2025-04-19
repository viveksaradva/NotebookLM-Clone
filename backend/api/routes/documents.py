from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel

from backend.db.database import get_db
from backend.schemas.documents import DocumentResponse, DocumentDetail
from backend.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])

document_service = DocumentService()

@router.post("/upload-pdf", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    session_id: str = Query(..., description="Unique session ID"),
    db: Session = Depends(get_db)
):
    """Upload a PDF document."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )

    try:
        # Use session_id as user_id for simplicity
        user_id = 1  # Default user ID since we removed authentication
        result = document_service.process_pdf(file.file, file.filename, db, user_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing PDF: {str(e)}"
        )

class WebArticleRequest(BaseModel):
    url: str

@router.post("/add-web-article", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_web_article(
    url: Optional[str] = Form(None),
    session_id: str = Query(..., description="Unique session ID"),
    db: Session = Depends(get_db),
    url_query: Optional[str] = Query(None, alias="url"),
    body: Optional[WebArticleRequest] = None
):
    """Add a web article."""
    # Get URL from form data, query parameter, or request body
    article_url = url or url_query

    # Check if URL is in the request body
    if not article_url and body and hasattr(body, 'url'):
        article_url = body.url

    if not article_url:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="URL is required. Please provide it either in the form data, as a query parameter, or in the request body."
        )

    try:
        # Use session_id as user_id for simplicity
        user_id = 1  # Default user ID since we removed authentication
        result = document_service.process_web_article(article_url, db, user_id)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing web article: {str(e)}"
        )

@router.get("/", response_model=List[DocumentResponse])
async def get_user_documents(
    session_id: str = Query(..., description="Unique session ID"),
    db: Session = Depends(get_db)
):
    """Get all documents."""
    # Use session_id as user_id for simplicity
    user_id = 1  # Default user ID since we removed authentication
    return document_service.get_user_documents(db, user_id)

@router.get("/{document_id}", response_model=DocumentDetail)
async def get_document(
    document_id: str,
    session_id: str = Query(..., description="Unique session ID"),
    db: Session = Depends(get_db)
):
    """Get a document by ID."""
    document = document_service.get_document(db, document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )

    # No authorization check since we removed authentication
    return document

@router.get("/{document_id}/chunks", response_model=List[str])
async def get_document_chunks(
    document_id: str,
    session_id: str = Query(..., description="Unique session ID"),
    db: Session = Depends(get_db)
):
    """Get all chunks for a document."""
    document = document_service.get_document(db, document_id)

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found"
        )

    # No authorization check since we removed authentication
    return document_service.get_document_chunks(document_id)
