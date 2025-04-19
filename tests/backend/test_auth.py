import pytest
from fastapi import status

def test_register_user(client):
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data

def test_register_user_duplicate_username(client, test_user):
    """Test user registration with duplicate username."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "another@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_register_user_duplicate_email(client, test_user):
    """Test user registration with duplicate email."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "anotheruser",
            "email": "test@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_login_user(client, test_user):
    """Test user login."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "password123"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_user_invalid_credentials(client):
    """Test user login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "testuser",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_current_user(authorized_client, test_user):
    """Test getting current user."""
    response = authorized_client.get("/api/v1/auth/me")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email
    assert data["id"] == test_user.id

def test_get_current_user_invalid_token(client):
    """Test getting current user with invalid token."""
    client.headers = {
        **client.headers,
        "Authorization": "Bearer invalidtoken"
    }
    
    response = client.get("/api/v1/auth/me")
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
