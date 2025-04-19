from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from backend.db.models import Highlight, Document
from backend.services.llm_service import LLMService

class HighlightService:
    def __init__(self):
        self.llm_service = LLMService()
    
    def create_highlight(self, db: Session, text: str, document_id: str, user_id: int, 
                         highlight_type: Optional[str] = None, 
                         sentence_type: Optional[str] = None, 
                         note: Optional[str] = None) -> Highlight:
        """Create a new highlight."""
        # Get the document
        document = db.query(Document).filter(Document.document_id == document_id).first()
        if not document:
            raise ValueError(f"Document with ID {document_id} not found")
        
        # Create highlight
        db_highlight = Highlight(
            text=text,
            highlight_type=highlight_type,
            sentence_type=sentence_type,
            note=note,
            document_id=document.id,
            user_id=user_id
        )
        
        # Save to database
        db.add(db_highlight)
        db.commit()
        db.refresh(db_highlight)
        
        return db_highlight
    
    def get_smart_highlight(self, text: str) -> Dict[str, Any]:
        """Generate a smart highlight using LLM."""
        return self.llm_service.generate_smart_highlight(text)
    
    def get_user_highlights(self, db: Session, user_id: int) -> List[Highlight]:
        """Get all highlights for a user."""
        return db.query(Highlight).filter(Highlight.user_id == user_id).all()
    
    def get_document_highlights(self, db: Session, document_id: str, user_id: int) -> List[Highlight]:
        """Get all highlights for a document."""
        document = db.query(Document).filter(Document.document_id == document_id).first()
        if not document:
            return []
        
        return db.query(Highlight).filter(
            Highlight.document_id == document.id,
            Highlight.user_id == user_id
        ).all()
    
    def delete_highlight(self, db: Session, highlight_id: int, user_id: int) -> bool:
        """Delete a highlight."""
        highlight = db.query(Highlight).filter(
            Highlight.id == highlight_id,
            Highlight.user_id == user_id
        ).first()
        
        if not highlight:
            return False
        
        db.delete(highlight)
        db.commit()
        
        return True
