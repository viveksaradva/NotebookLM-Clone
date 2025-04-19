from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict
import uuid
import os
from datetime import datetime, timedelta

# Create FastAPI app
app = FastAPI(
    title="DocuMind API",
    version="1.0.0",
    description="AI-Powered Knowledge Management API"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# In-memory storage
users = {
    "token_12345": {
        "id": 1,
        "username": "vivek",
        "email": "vivek@example.com",
        "password": "vivek@123",  # In a real app, this would be hashed
        "is_active": True,
        "created_at": datetime.now()
    }
}
documents = {}
highlights = {}
chat_sessions = {}

# Models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Helper functions
def get_current_user(token: str = Depends(oauth2_scheme)):
    if token not in users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return users[token]

# Routes
@app.post("/api/v1/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate):
    # Print debug info
    print(f"Registration attempt for user: {user.username}")
    print(f"Current users in memory: {users}")

    # Check if username already exists
    for token, existing_user in users.items():
        if existing_user["username"] == user.username:
            print(f"Registration failed: Username {user.username} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Username {user.username} already registered"
            )

    # Create user
    user_id = len(users) + 1
    token = f"token_{uuid.uuid4().hex}"
    users[token] = {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "password": user.password,  # In a real app, this would be hashed
        "is_active": True,
        "created_at": datetime.now()
    }

    print(f"Registration successful for user: {user.username}")
    print(f"Updated users in memory: {users}")

    return {
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "is_active": True,
        "created_at": datetime.now()
    }

@app.post("/api/v1/auth/login", response_model=Token)
def login(user_login: UserLogin):
    # Print debug info
    print(f"Login attempt for user: {user_login.username}")
    print(f"Current users in memory: {users}")

    # Check credentials
    for token, user in users.items():
        if user["username"] == user_login.username and user["password"] == user_login.password:
            print(f"Login successful for user: {user_login.username}")
            return {
                "access_token": token,
                "token_type": "bearer"
            }

    print(f"Login failed for user: {user_login.username}")
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

@app.get("/api/v1/auth/me", response_model=UserResponse)
def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return {
        "id": current_user["id"],
        "username": current_user["username"],
        "email": current_user["email"],
        "is_active": current_user["is_active"],
        "created_at": current_user["created_at"]
    }

@app.get("/")
def read_root():
    return {
        "app_name": "DocuMind API",
        "version": "1.0.0",
        "description": "AI-Powered Knowledge Management API"
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/v1/documents/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """Upload a PDF document."""
    # Create upload directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)

    # Generate a unique document ID
    document_id = f"doc_{uuid.uuid4().hex}"

    # Save the file
    file_path = f"uploads/{document_id}.pdf"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Create document record
    documents[document_id] = {
        "id": len(documents) + 1,
        "title": file.filename,
        "document_id": document_id,
        "file_path": file_path,
        "file_type": "pdf",
        "chunk_count": 0,
        "owner_id": current_user["id"],
        "created_at": datetime.now()
    }

    return {
        "message": f"PDF '{file.filename}' uploaded successfully!",
        "document_id": document_id,
        "indexed_documents": 0
    }

@app.get("/api/v1/documents")
def get_user_documents(current_user: dict = Depends(get_current_user)):
    """Get all documents for the current user."""
    user_documents = []
    for doc_id, doc in documents.items():
        if doc["owner_id"] == current_user["id"]:
            user_documents.append({
                "id": doc["id"],
                "title": doc["title"],
                "document_id": doc["document_id"],
                "file_type": doc["file_type"],
                "created_at": doc["created_at"]
            })

    return user_documents

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9000)
