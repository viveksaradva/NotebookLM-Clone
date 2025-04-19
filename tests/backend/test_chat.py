import pytest
from unittest.mock import patch, MagicMock

from backend.services.chat_service import ChatService

@pytest.fixture
def chat_service():
    """Create a ChatService with mocked dependencies."""
    with patch("backend.services.chat_service.VectorDBService") as mock_vectordb, \
         patch("backend.services.chat_service.LLMService") as mock_llm, \
         patch("backend.services.chat_service.get_session_memory") as mock_get_memory, \
         patch("backend.services.chat_service.reset_session_memory") as mock_reset_memory:
        
        service = ChatService()
        service.vectordb_service = mock_vectordb.return_value
        service.llm_service = mock_llm.return_value
        
        # Mock memory
        mock_memory = MagicMock()
        mock_memory.load_memory_variables.return_value = {"history": []}
        mock_get_memory.return_value = mock_memory
        
        yield service

@patch("uuid.uuid4")
def test_create_session(mock_uuid, chat_service):
    """Test creating a new chat session."""
    # Mock UUID
    mock_uuid.return_value.hex = "12345678" * 4
    
    # Create a session
    result = chat_service.create_session(document_id="test_doc")
    
    # Check the result
    assert result["session_id"] == "session_12345678"
    assert result["document_id"] == "test_doc"
    assert result["message"] == "Chat session created successfully."

@patch("uuid.uuid4")
def test_process_query_new_session(mock_uuid, chat_service):
    """Test processing a query with a new session."""
    # Mock UUID
    mock_uuid.return_value.hex = "12345678" * 4
    
    # Mock VectorDBService
    chat_service.vectordb_service.hybrid_query.return_value = (
        ["Document 1", "Document 2"],
        [{"keywords": ["key1", "key2"]}, {"keywords": ["key3", "key4"]}]
    )
    
    # Mock LLMService
    chat_service.llm_service.generate_rag_response.return_value = "This is a test response."
    
    # Process a query
    result = chat_service.process_query(
        query="What is RAG?",
        document_id="test_doc"
    )
    
    # Check the result
    assert result["query"] == "What is RAG?"
    assert result["response"] == "This is a test response."
    assert result["session_id"] == "session_12345678"

def test_process_query_existing_session(chat_service):
    """Test processing a query with an existing session."""
    # Mock VectorDBService
    chat_service.vectordb_service.hybrid_query.return_value = (
        ["Document 1", "Document 2"],
        [{"keywords": ["key1", "key2"]}, {"keywords": ["key3", "key4"]}]
    )
    
    # Mock LLMService
    chat_service.llm_service.generate_rag_response.return_value = "This is a test response."
    
    # Process a query
    result = chat_service.process_query(
        query="What is RAG?",
        document_id="test_doc",
        session_id="existing_session"
    )
    
    # Check the result
    assert result["query"] == "What is RAG?"
    assert result["response"] == "This is a test response."
    assert result["session_id"] == "existing_session"

def test_reset_session(chat_service):
    """Test resetting a chat session."""
    # Reset a session
    result = chat_service.reset_session(session_id="test_session")
    
    # Check the result
    assert "message" in result
