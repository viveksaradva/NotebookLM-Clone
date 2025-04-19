import pytest
from unittest.mock import patch, MagicMock

from backend.services.llm_service import LLMService

@pytest.fixture
def llm_service():
    """Create an LLMService with mocked clients."""
    with patch("backend.services.llm_service.Together") as mock_together, \
         patch("backend.services.llm_service.Groq") as mock_groq, \
         patch("backend.services.llm_service.ChatTogether") as mock_chat_together:
        
        service = LLMService()
        service.together_client = mock_together.return_value
        service.groq_client = mock_groq.return_value
        service.together_chat = mock_chat_together.return_value
        
        yield service

def test_get_together_response(llm_service):
    """Test getting a response from Together AI."""
    # Mock the response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "This is a test response."
    llm_service.together_client.chat.completions.create.return_value = mock_response
    
    # Get the response
    response = llm_service.get_together_response("This is a test prompt.")
    
    # Check the response
    assert response == "This is a test response."
    llm_service.together_client.chat.completions.create.assert_called_once()

def test_get_groq_response(llm_service):
    """Test getting a response from Groq."""
    # Mock the response
    mock_response = MagicMock()
    mock_response.choices[0].message.content = "This is a test response."
    llm_service.groq_client.chat.completions.create.return_value = mock_response
    
    # Get the response
    response = llm_service.get_groq_response("This is a test prompt.")
    
    # Check the response
    assert response == "This is a test response."
    llm_service.groq_client.chat.completions.create.assert_called_once()

def test_generate_rag_response(llm_service):
    """Test generating a RAG response."""
    # Mock the response
    llm_service.get_together_response = MagicMock(return_value="This is a RAG response.")
    
    # Generate the response
    response = llm_service.generate_rag_response(
        query="What is RAG?",
        context="RAG stands for Retrieval-Augmented Generation."
    )
    
    # Check the response
    assert response == "This is a RAG response."
    llm_service.get_together_response.assert_called_once()

def test_generate_smart_highlight(llm_service):
    """Test generating a smart highlight."""
    # Mock the response
    llm_service.get_groq_response = MagicMock(
        return_value='{"highlight_type": "Concept", "sentence_type": "Definition", "short_note": "This is a test note."}'
    )
    
    # Generate the smart highlight
    result = llm_service.generate_smart_highlight("This is a test text.")
    
    # Check the result
    assert result["highlight_type"] == "Concept"
    assert result["sentence_type"] == "Definition"
    assert result["short_note"] == "This is a test note."
    llm_service.get_groq_response.assert_called_once()

def test_generate_semantic_summary(llm_service):
    """Test generating a semantic summary."""
    # Mock the response
    llm_service.get_groq_response = MagicMock(
        return_value='{"compressed_study_memory": "This is a test summary."}'
    )
    
    # Generate the semantic summary
    result = llm_service.generate_semantic_summary(["Highlight 1", "Highlight 2"])
    
    # Check the result
    assert result["compressed_study_memory"] == "This is a test summary."
    llm_service.get_groq_response.assert_called_once()

def test_generate_study_guide(llm_service):
    """Test generating a study guide."""
    # Mock the responses
    llm_service.get_together_response = MagicMock(side_effect=[
        "This is a test study guide.",
        '["Key concept 1", "Key concept 2"]',
        '["Question 1", "Question 2"]'
    ])
    
    # Generate the study guide
    result = llm_service.generate_study_guide(["Chunk 1", "Chunk 2"])
    
    # Check the result
    assert result["study_guide"] == "This is a test study guide."
    assert result["key_concepts"] == ["Key concept 1", "Key concept 2"]
    assert result["review_questions"] == ["Question 1", "Question 2"]
    assert llm_service.get_together_response.call_count == 3
