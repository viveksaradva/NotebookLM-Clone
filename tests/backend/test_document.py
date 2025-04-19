import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from io import BytesIO

from backend.services.document_service import DocumentService
from backend.db.models import Document

@pytest.fixture
def document_service():
    """Create a DocumentService with mocked dependencies."""
    with patch("backend.services.document_service.VectorDBService") as mock_vectordb:
        service = DocumentService()
        service.vectordb_service = mock_vectordb.return_value
        
        # Create a temporary directory for uploads
        with tempfile.TemporaryDirectory() as temp_dir:
            service.upload_dir = temp_dir
            yield service

def test_save_uploaded_file(document_service):
    """Test saving an uploaded file."""
    # Create a test file
    file_content = b"This is a test file."
    file = BytesIO(file_content)
    filename = "test.pdf"
    
    # Save the file
    document_id, file_path = document_service.save_uploaded_file(file, filename)
    
    # Check the result
    assert document_id is not None
    assert os.path.exists(file_path)
    
    # Check the file content
    with open(file_path, "rb") as f:
        assert f.read() == file_content

@patch("uuid.uuid4")
def test_process_pdf(mock_uuid, document_service, db):
    """Test processing a PDF file."""
    # Mock UUID
    mock_uuid.return_value.hex = "12345678" * 4
    
    # Mock VectorDBService
    document_service.vectordb_service.add_pdf.return_value = 10
    
    # Create a test file
    file_content = b"This is a test PDF."
    file = BytesIO(file_content)
    filename = "test.pdf"
    
    # Process the PDF
    result = document_service.process_pdf(file, filename, db, user_id=1)
    
    # Check the result
    assert result["message"] == "PDF 'test.pdf' uploaded successfully!"
    assert result["document_id"] == "12345678"
    assert result["indexed_documents"] == 10
    
    # Check the database
    document = db.query(Document).filter(Document.document_id == "12345678").first()
    assert document is not None
    assert document.title == filename
    assert document.file_type == "pdf"
    assert document.chunk_count == 10
    assert document.owner_id == 1

@patch("uuid.uuid4")
def test_process_web_article(mock_uuid, document_service, db):
    """Test processing a web article."""
    # Mock UUID
    mock_uuid.return_value.hex = "12345678" * 4
    
    # Mock VectorDBService
    document_service.vectordb_service.add_web_article.return_value = {
        "message": "Web article added successfully!",
        "document_id": "12345678",
        "chunk_count": 5,
        "metadata": {
            "url": "https://example.com",
            "title": "Example Article",
            "description": "This is an example article."
        }
    }
    
    # Process the web article
    result = document_service.process_web_article("https://example.com", db, user_id=1)
    
    # Check the result
    assert result["message"] == "Web article added successfully!"
    assert result["document_id"] == "12345678"
    assert result["title"] == "Example Article"
    assert result["indexed_documents"] == 5
    
    # Check the database
    document = db.query(Document).filter(Document.document_id == "12345678").first()
    assert document is not None
    assert document.title == "Example Article"
    assert document.file_type == "web"
    assert document.chunk_count == 5
    assert document.owner_id == 1

def test_get_user_documents(document_service, db):
    """Test getting all documents for a user."""
    # Create test documents
    documents = [
        Document(
            title=f"Document {i}",
            document_id=f"doc_{i}",
            file_path=f"/path/to/doc_{i}",
            file_type="pdf",
            chunk_count=5,
            owner_id=1
        )
        for i in range(3)
    ]
    
    db.add_all(documents)
    db.commit()
    
    # Get the documents
    result = document_service.get_user_documents(db, user_id=1)
    
    # Check the result
    assert len(result) == 3
    assert result[0].title == "Document 0"
    assert result[1].title == "Document 1"
    assert result[2].title == "Document 2"

def test_get_document(document_service, db):
    """Test getting a document by ID."""
    # Create a test document
    document = Document(
        title="Test Document",
        document_id="test_doc",
        file_path="/path/to/test_doc",
        file_type="pdf",
        chunk_count=5,
        owner_id=1
    )
    
    db.add(document)
    db.commit()
    
    # Get the document
    result = document_service.get_document(db, document_id="test_doc")
    
    # Check the result
    assert result is not None
    assert result.title == "Test Document"
    assert result.document_id == "test_doc"
    assert result.file_type == "pdf"
    assert result.chunk_count == 5
    assert result.owner_id == 1

def test_get_document_chunks(document_service):
    """Test getting all chunks for a document."""
    # Mock VectorDBService
    document_service.vectordb_service.get_documents.return_value = [
        "Chunk 1",
        "Chunk 2",
        "Chunk 3"
    ]
    
    # Get the chunks
    result = document_service.get_document_chunks(document_id="test_doc")
    
    # Check the result
    assert len(result) == 3
    assert result[0] == "Chunk 1"
    assert result[1] == "Chunk 2"
    assert result[2] == "Chunk 3"
