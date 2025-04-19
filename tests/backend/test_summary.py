import pytest
from unittest.mock import patch, MagicMock

from backend.services.summary_service import SummaryService

@pytest.fixture
def summary_service():
    """Create a SummaryService with mocked dependencies."""
    with patch("backend.services.summary_service.VectorDBService") as mock_vectordb, \
         patch("backend.services.summary_service.LLMService") as mock_llm:
        
        service = SummaryService()
        service.vectordb_service = mock_vectordb.return_value
        service.llm_service = mock_llm.return_value
        
        yield service

def test_generate_document_summary(summary_service):
    """Test generating a summary for a document."""
    # Mock VectorDBService
    summary_service.vectordb_service.get_documents.return_value = [
        "Chunk 1",
        "Chunk 2",
        "Chunk 3"
    ]
    
    # Mock LLMService
    summary_service.llm_service.get_together_response.return_value = "This is a test summary."
    
    # Generate a summary
    result = summary_service.generate_document_summary(document_id="test_doc")
    
    # Check the result
    assert result["document_id"] == "test_doc"
    assert result["summary"] == "This is a test summary."

def test_generate_document_summary_no_chunks(summary_service):
    """Test generating a summary for a document with no chunks."""
    # Mock VectorDBService
    summary_service.vectordb_service.get_documents.return_value = []
    
    # Generate a summary
    result = summary_service.generate_document_summary(document_id="test_doc")
    
    # Check the result
    assert result["document_id"] == "test_doc"
    assert result["summary"] == "No document content found."

def test_generate_semantic_summary(summary_service):
    """Test generating a semantic summary from highlights."""
    # Mock LLMService
    summary_service.llm_service.generate_semantic_summary.return_value = {
        "compressed_study_memory": "This is a test semantic summary."
    }
    
    # Generate a semantic summary
    result = summary_service.generate_semantic_summary(highlights=["Highlight 1", "Highlight 2"])
    
    # Check the result
    assert result["compressed_study_memory"] == "This is a test semantic summary."
