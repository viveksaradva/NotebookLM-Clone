import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock

from backend.services.vectordb_service import VectorDBService

@pytest.fixture
def vectordb_service():
    """Create a VectorDBService with a temporary directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        service = VectorDBService(persist_dir=temp_dir)
        yield service

@pytest.fixture
def sample_chunks():
    """Create sample document chunks."""
    return [
        {
            "text": "This is the first chunk of text.",
            "embedding": [0.1, 0.2, 0.3],
            "keywords": ["first", "chunk", "text"]
        },
        {
            "text": "This is the second chunk of text.",
            "embedding": [0.4, 0.5, 0.6],
            "keywords": ["second", "chunk", "text"]
        }
    ]

@patch("backend.services.vectordb_service.Embedder")
def test_add_document(mock_embedder, vectordb_service, sample_chunks):
    """Test adding a document to the vector database."""
    document_id = "test_doc"
    
    # Mock the collection
    mock_collection = MagicMock()
    vectordb_service.client.get_or_create_collection = MagicMock(return_value=mock_collection)
    mock_collection.count.return_value = len(sample_chunks)
    
    # Add the document
    result = vectordb_service.add_document(document_id, sample_chunks)
    
    # Check the result
    assert result == len(sample_chunks)
    assert mock_collection.add.call_count == 1

@patch("backend.services.vectordb_service.Embedder")
def test_query(mock_embedder, vectordb_service):
    """Test querying the vector database."""
    document_id = "test_doc"
    query_text = "test query"
    
    # Mock the embedder
    mock_embedder_instance = MagicMock()
    mock_embedder.return_value = mock_embedder_instance
    mock_embedder_instance.get_embedding.return_value = [0.1, 0.2, 0.3]
    
    # Mock the collection
    mock_collection = MagicMock()
    vectordb_service.client.get_collection = MagicMock(return_value=mock_collection)
    mock_collection.count.return_value = 2
    mock_collection.query.return_value = {
        "documents": [["doc1", "doc2"]],
        "metadatas": [[{"keywords": "first, chunk"}, {"keywords": "second, chunk"}]],
        "ids": [["id1", "id2"]]
    }
    
    # Query the database
    result = vectordb_service.query(query_text, document_id)
    
    # Check the result
    assert "documents" in result
    assert "metadatas" in result
    assert "ids" in result
    assert len(result["documents"]) == 1
    assert len(result["documents"][0]) == 2

@patch("backend.services.vectordb_service.Embedder")
def test_hybrid_query(mock_embedder, vectordb_service):
    """Test hybrid querying the vector database."""
    document_id = "test_doc"
    query_text = "test query"
    
    # Mock the embedder
    mock_embedder_instance = MagicMock()
    mock_embedder.return_value = mock_embedder_instance
    mock_embedder_instance.get_embedding.return_value = [0.1, 0.2, 0.3]
    
    # Mock the collection
    mock_collection = MagicMock()
    vectordb_service._get_collection = MagicMock(return_value=mock_collection)
    mock_collection.count.return_value = 2
    mock_collection.query.return_value = {
        "documents": [["doc1", "doc2"]],
        "metadatas": [[{"keywords": "first, chunk"}, {"keywords": "second, chunk"}]],
        "ids": [["id1", "id2"]]
    }
    
    # Query the database
    docs, metadata = vectordb_service.hybrid_query(query_text, document_id)
    
    # Check the result
    assert len(docs) == 2
    assert len(metadata) == 2
