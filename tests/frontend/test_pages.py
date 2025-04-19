import pytest
from unittest.mock import patch, MagicMock
import streamlit as st
import requests

# Note: Testing Streamlit apps is challenging because they run in a special way.
# These tests are more like integration tests that check the API calls made by the frontend.

@pytest.fixture
def mock_requests():
    """Mock requests module."""
    with patch("frontend.main.requests") as mock_req:
        yield mock_req

@pytest.fixture
def mock_streamlit():
    """Mock streamlit module."""
    with patch("frontend.main.st") as mock_st:
        yield mock_st

def test_login(mock_requests, mock_streamlit):
    """Test login functionality."""
    # Mock the API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "access_token": "test_token",
        "token_type": "bearer"
    }
    mock_requests.post.return_value = mock_response
    
    # Import the login function
    from frontend.main import login
    
    # Call the login function
    result = login("testuser", "password123")
    
    # Check the result
    assert result is True
    mock_requests.post.assert_called_once()
    
    # Check that the token was stored in session state
    assert st.session_state.token == "test_token"

def test_login_failure(mock_requests, mock_streamlit):
    """Test login failure."""
    # Mock the API response
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Invalid credentials"
    mock_requests.post.return_value = mock_response
    
    # Import the login function
    from frontend.main import login
    
    # Call the login function
    result = login("testuser", "wrongpassword")
    
    # Check the result
    assert result is False
    mock_requests.post.assert_called_once()
    
    # Check that the token was not stored in session state
    assert "token" not in st.session_state or st.session_state.token is None

def test_register(mock_requests, mock_streamlit):
    """Test registration functionality."""
    # Mock the API response
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "username": "testuser",
        "email": "test@example.com",
        "id": 1
    }
    mock_requests.post.return_value = mock_response
    
    # Import the register function
    from frontend.main import register
    
    # Call the register function
    result = register("testuser", "test@example.com", "password123")
    
    # Check the result
    assert result is True
    mock_requests.post.assert_called_once()

def test_register_failure(mock_requests, mock_streamlit):
    """Test registration failure."""
    # Mock the API response
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Username already registered"
    mock_requests.post.return_value = mock_response
    
    # Import the register function
    from frontend.main import register
    
    # Call the register function
    result = register("testuser", "test@example.com", "password123")
    
    # Check the result
    assert result is False
    mock_requests.post.assert_called_once()

def test_upload_pdf(mock_requests, mock_streamlit):
    """Test PDF upload functionality."""
    # Mock the API response
    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {
        "message": "PDF 'test.pdf' uploaded successfully!",
        "document_id": "test_doc",
        "indexed_documents": 10
    }
    mock_requests.post.return_value = mock_response
    
    # Import the upload_pdf function
    from frontend.main import upload_pdf
    
    # Create a mock file
    mock_file = MagicMock()
    
    # Call the upload_pdf function
    result = upload_pdf(mock_file)
    
    # Check the result
    assert result is not None
    assert result["document_id"] == "test_doc"
    mock_requests.post.assert_called_once()
    
    # Check that the document ID was stored in session state
    assert st.session_state.current_document_id == "test_doc"

def test_query_document(mock_requests, mock_streamlit):
    """Test document querying functionality."""
    # Mock the API response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "query": "What is RAG?",
        "response": "RAG stands for Retrieval-Augmented Generation.",
        "session_id": "test_session",
        "chat_history": []
    }
    mock_requests.post.return_value = mock_response
    
    # Import the query_document function
    from frontend.main import query_document
    
    # Call the query_document function
    result = query_document(
        query="What is RAG?",
        document_id="test_doc",
        session_id="test_session"
    )
    
    # Check the result
    assert result is not None
    assert result["query"] == "What is RAG?"
    assert result["response"] == "RAG stands for Retrieval-Augmented Generation."
    assert result["session_id"] == "test_session"
    mock_requests.post.assert_called_once()
    
    # Check that the session ID was stored in session state
    assert st.session_state.chat_session_id == "test_session"
