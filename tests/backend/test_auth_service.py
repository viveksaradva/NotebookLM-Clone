import pytest
from unittest.mock import patch, MagicMock

from backend.services.auth_service import AuthService
from backend.db.models import User

@pytest.fixture
def auth_service():
    """Create an AuthService."""
    return AuthService()

def test_create_user(auth_service, db):
    """Test creating a new user."""
    # Create a user
    result = auth_service.create_user(
        db=db,
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Check the result
    assert result is not None
    assert result.username == "testuser"
    assert result.email == "test@example.com"
    assert result.hashed_password != "password123"  # Password should be hashed
    
    # Check the database
    user = db.query(User).filter(User.username == "testuser").first()
    assert user is not None
    assert user.email == "test@example.com"

def test_create_user_duplicate_username(auth_service, db):
    """Test creating a user with a duplicate username."""
    # Create a user
    auth_service.create_user(
        db=db,
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Try to create another user with the same username
    with pytest.raises(ValueError):
        auth_service.create_user(
            db=db,
            username="testuser",
            email="another@example.com",
            password="password123"
        )

def test_create_user_duplicate_email(auth_service, db):
    """Test creating a user with a duplicate email."""
    # Create a user
    auth_service.create_user(
        db=db,
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Try to create another user with the same email
    with pytest.raises(ValueError):
        auth_service.create_user(
            db=db,
            username="anotheruser",
            email="test@example.com",
            password="password123"
        )

def test_authenticate_user(auth_service, db):
    """Test authenticating a user."""
    # Create a user
    auth_service.create_user(
        db=db,
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Authenticate the user
    user = auth_service.authenticate_user(
        db=db,
        username="testuser",
        password="password123"
    )
    
    # Check the result
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"

def test_authenticate_user_invalid_username(auth_service, db):
    """Test authenticating a user with an invalid username."""
    # Create a user
    auth_service.create_user(
        db=db,
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Try to authenticate with an invalid username
    user = auth_service.authenticate_user(
        db=db,
        username="invaliduser",
        password="password123"
    )
    
    # Check the result
    assert user is None

def test_authenticate_user_invalid_password(auth_service, db):
    """Test authenticating a user with an invalid password."""
    # Create a user
    auth_service.create_user(
        db=db,
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Try to authenticate with an invalid password
    user = auth_service.authenticate_user(
        db=db,
        username="testuser",
        password="invalidpassword"
    )
    
    # Check the result
    assert user is None

@patch("backend.services.auth_service.create_access_token")
def test_create_user_token(mock_create_token, auth_service):
    """Test creating an access token for a user."""
    # Mock create_access_token
    mock_create_token.return_value = "test_token"
    
    # Create a user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password"
    )
    
    # Create a token
    result = auth_service.create_user_token(user)
    
    # Check the result
    assert result["access_token"] == "test_token"
    assert result["token_type"] == "bearer"

def test_get_user_by_username(auth_service, db):
    """Test getting a user by username."""
    # Create a user
    auth_service.create_user(
        db=db,
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Get the user
    user = auth_service.get_user_by_username(db, username="testuser")
    
    # Check the result
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"

def test_get_user_by_email(auth_service, db):
    """Test getting a user by email."""
    # Create a user
    auth_service.create_user(
        db=db,
        username="testuser",
        email="test@example.com",
        password="password123"
    )
    
    # Get the user
    user = auth_service.get_user_by_email(db, email="test@example.com")
    
    # Check the result
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
