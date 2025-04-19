import os
import uuid
from typing import Dict, Any, List, Optional, BinaryIO
from sqlalchemy.orm import Session

from backend.db.models import Document, User
from backend.services.vectordb_service import VectorDBService

class DocumentService:
    def __init__(self):
        self.vectordb_service = VectorDBService()
        self.upload_dir = "data"
    
    def save_uploaded_file(self, file: BinaryIO, filename: str) -> str:
        """Save an uploaded file to disk."""
        # Create a unique document ID
        document_id = uuid.uuid4().hex[:8]
        
        # Create the upload directory if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(self.upload_dir, f"{document_id}_{filename}")
        with open(file_path, "wb") as buffer:
            buffer.write(file.read())
        
        return document_id, file_path
    
    def process_pdf(self, file: BinaryIO, filename: str, db: Session, user_id: int) -> Dict[str, Any]:
        """Process a PDF file and store it in the database."""
        # Save the file
        document_id, file_path = self.save_uploaded_file(file, filename)
        
        # Process the PDF
        chunk_count = self.vectordb_service.add_pdf(file_path, document_id)
        
        # Create a document record
        db_document = Document(
            title=filename,
            document_id=document_id,
            file_path=file_path,
            file_type="pdf",
            chunk_count=chunk_count,
            owner_id=user_id
        )
        
        # Save to database
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        return {
            "message": f"PDF '{filename}' uploaded successfully!",
            "document_id": document_id,
            "indexed_documents": chunk_count
        }
    
    def process_web_article(self, url: str, db: Session, user_id: int) -> Dict[str, Any]:
        """Process a web article and store it in the database."""
        # Create a unique document ID
        document_id = uuid.uuid4().hex[:8]
        
        # Process the web article
        result = self.vectordb_service.add_web_article(url, document_id)
        
        # Extract metadata
        metadata = result["metadata"]
        title = metadata.get("title", url)
        
        # Create a document record
        db_document = Document(
            title=title,
            document_id=document_id,
            file_path=url,
            file_type="web",
            chunk_count=result["chunk_count"],
            owner_id=user_id
        )
        
        # Save to database
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        return {
            "message": "Web article added successfully!",
            "document_id": document_id,
            "title": title,
            "indexed_documents": result["chunk_count"]
        }
    
    def get_user_documents(self, db: Session, user_id: int) -> List[Document]:
        """Get all documents for a user."""
        return db.query(Document).filter(Document.owner_id == user_id).all()
    
    def get_document(self, db: Session, document_id: str) -> Optional[Document]:
        """Get a document by ID."""
        return db.query(Document).filter(Document.document_id == document_id).first()
    
    def get_document_chunks(self, document_id: str) -> List[str]:
        """Get all chunks for a document."""
        return self.vectordb_service.get_documents(document_id)
