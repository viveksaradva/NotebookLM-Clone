import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.api.main import app
from backend.db.database import Base, get_db
from backend.db.models import User
from backend.core.security import get_password_hash

# Create a test database in memory
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session for each test
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop the database tables
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    # Override the get_db dependency
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Create a test client
    with TestClient(app) as c:
        yield c
    
    # Reset the dependency override
    app.dependency_overrides = {}

@pytest.fixture(scope="function")
def test_user(db):
    # Create a test user
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("password123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

@pytest.fixture(scope="function")
def token(client, test_user):
    # Get a token for the test user
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testuser", "password": "password123"}
    )
    
    return response.json()["access_token"]

@pytest.fixture(scope="function")
def authorized_client(client, token):
    # Create an authorized client
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    
    return client
