import pytest
from unittest.mock import patch, MagicMock

from backend.services.study_guide_service import StudyGuideService

@pytest.fixture
def study_guide_service():
    """Create a StudyGuideService with mocked dependencies."""
    with patch("backend.services.study_guide_service.VectorDBService") as mock_vectordb, \
         patch("backend.services.study_guide_service.LLMService") as mock_llm:
        
        service = StudyGuideService()
        service.vectordb_service = mock_vectordb.return_value
        service.llm_service = mock_llm.return_value
        
        yield service

def test_generate_study_guide(study_guide_service):
    """Test generating a study guide for a document."""
    # Mock VectorDBService
    study_guide_service.vectordb_service.get_documents.return_value = [
        "Chunk 1",
        "Chunk 2",
        "Chunk 3"
    ]
    
    # Mock LLMService
    study_guide_service.llm_service.generate_study_guide.return_value = {
        "study_guide": "This is a test study guide.",
        "key_concepts": ["Concept 1", "Concept 2"],
        "review_questions": ["Question 1", "Question 2"]
    }
    
    # Generate a study guide
    result = study_guide_service.generate_study_guide(document_id="test_doc")
    
    # Check the result
    assert result["document_id"] == "test_doc"
    assert result["study_guide"] == "This is a test study guide."
    assert result["key_concepts"] == ["Concept 1", "Concept 2"]
    assert result["review_questions"] == ["Question 1", "Question 2"]

def test_generate_study_guide_no_chunks(study_guide_service):
    """Test generating a study guide for a document with no chunks."""
    # Mock VectorDBService
    study_guide_service.vectordb_service.get_documents.return_value = []
    
    # Generate a study guide
    result = study_guide_service.generate_study_guide(document_id="test_doc")
    
    # Check the result
    assert result["document_id"] == "test_doc"
    assert result["study_guide"] == "No document content found."
    assert result["key_concepts"] == []
    assert result["review_questions"] == []
