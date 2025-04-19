from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.schemas.auth import UserCreate, UserLogin, UserResponse, Token
from backend.services.auth_service import AuthService
from backend.core.security import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

auth_service = AuthService()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    try:
        db_user = auth_service.create_user(db, user.username, user.email, user.password)
        return db_user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login a user."""
    db_user = auth_service.authenticate_user(db, user.username, user.password)
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return auth_service.create_user_token(db_user)

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """Get current user information."""
    return current_user
