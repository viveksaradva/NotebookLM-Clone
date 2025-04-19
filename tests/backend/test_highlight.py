import pytest
from unittest.mock import patch, MagicMock

from backend.services.highlight_service import HighlightService
from backend.db.models import Highlight, Document

@pytest.fixture
def highlight_service():
    """Create a HighlightService with mocked dependencies."""
    with patch("backend.services.highlight_service.LLMService") as mock_llm:
        service = HighlightService()
        service.llm_service = mock_llm.return_value
        yield service

def test_create_highlight(highlight_service, db):
    """Test creating a new highlight."""
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
    
    # Create a highlight
    result = highlight_service.create_highlight(
        db=db,
        text="This is a test highlight.",
        document_id="test_doc",
        user_id=1,
        highlight_type="Concept",
        sentence_type="Definition",
        note="This is a test note."
    )
    
    # Check the result
    assert result is not None
    assert result.text == "This is a test highlight."
    assert result.highlight_type == "Concept"
    assert result.sentence_type == "Definition"
    assert result.note == "This is a test note."
    assert result.document_id == document.id
    assert result.user_id == 1

def test_create_highlight_invalid_document(highlight_service, db):
    """Test creating a highlight with an invalid document."""
    # Try to create a highlight
    with pytest.raises(ValueError):
        highlight_service.create_highlight(
            db=db,
            text="This is a test highlight.",
            document_id="invalid_doc",
            user_id=1
        )

def test_get_smart_highlight(highlight_service):
    """Test generating a smart highlight."""
    # Mock LLMService
    highlight_service.llm_service.generate_smart_highlight.return_value = {
        "highlight_type": "Concept",
        "sentence_type": "Definition",
        "short_note": "This is a test note."
    }
    
    # Generate a smart highlight
    result = highlight_service.get_smart_highlight("This is a test text.")
    
    # Check the result
    assert result["highlight_type"] == "Concept"
    assert result["sentence_type"] == "Definition"
    assert result["short_note"] == "This is a test note."

def test_get_user_highlights(highlight_service, db):
    """Test getting all highlights for a user."""
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
    
    # Create test highlights
    highlights = [
        Highlight(
            text=f"Highlight {i}",
            highlight_type="Concept",
            sentence_type="Definition",
            note=f"Note {i}",
            document_id=document.id,
            user_id=1
        )
        for i in range(3)
    ]
    
    db.add_all(highlights)
    db.commit()
    
    # Get the highlights
    result = highlight_service.get_user_highlights(db, user_id=1)
    
    # Check the result
    assert len(result) == 3
    assert result[0].text == "Highlight 0"
    assert result[1].text == "Highlight 1"
    assert result[2].text == "Highlight 2"

def test_get_document_highlights(highlight_service, db):
    """Test getting all highlights for a document."""
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
    
    # Create test highlights
    highlights = [
        Highlight(
            text=f"Highlight {i}",
            highlight_type="Concept",
            sentence_type="Definition",
            note=f"Note {i}",
            document_id=document.id,
            user_id=1
        )
        for i in range(3)
    ]
    
    db.add_all(highlights)
    db.commit()
    
    # Get the highlights
    result = highlight_service.get_document_highlights(db, document_id="test_doc", user_id=1)
    
    # Check the result
    assert len(result) == 3
    assert result[0].text == "Highlight 0"
    assert result[1].text == "Highlight 1"
    assert result[2].text == "Highlight 2"

def test_delete_highlight(highlight_service, db):
    """Test deleting a highlight."""
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
    
    # Create a test highlight
    highlight = Highlight(
        text="Test Highlight",
        highlight_type="Concept",
        sentence_type="Definition",
        note="Test Note",
        document_id=document.id,
        user_id=1
    )
    
    db.add(highlight)
    db.commit()
    
    # Delete the highlight
    result = highlight_service.delete_highlight(db, highlight_id=highlight.id, user_id=1)
    
    # Check the result
    assert result is True
    
    # Check the database
    deleted_highlight = db.query(Highlight).filter(Highlight.id == highlight.id).first()
    assert deleted_highlight is None

def test_delete_highlight_not_found(highlight_service, db):
    """Test deleting a non-existent highlight."""
    # Delete a non-existent highlight
    result = highlight_service.delete_highlight(db, highlight_id=999, user_id=1)
    
    # Check the result
    assert result is False
