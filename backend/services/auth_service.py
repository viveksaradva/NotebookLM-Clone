from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import timedelta

from backend.db.models import User
from backend.core.security import get_password_hash, verify_password, create_access_token
from backend.core.config import settings

class AuthService:
    def create_user(self, db: Session, username: str, email: str, password: str) -> User:
        """Create a new user."""
        # Check if username already exists
        db_user = db.query(User).filter(User.username == username).first()
        if db_user:
            raise ValueError(f"Username {username} already registered")
        
        # Check if email already exists
        db_user = db.query(User).filter(User.email == email).first()
        if db_user:
            raise ValueError(f"Email {email} already registered")
        
        # Create user
        hashed_password = get_password_hash(password)
        db_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password
        )
        
        # Save to database
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    
    def authenticate_user(self, db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate a user."""
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        return user
    
    def create_user_token(self, user: User) -> Dict[str, Any]:
        """Create an access token for a user."""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    
    def get_user_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get a user by username."""
        return db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get a user by email."""
        return db.query(User).filter(User.email == email).first()
