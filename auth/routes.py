from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth import models, database 
from auth.utils.jwt import create_access_token
from auth.utils.dependencies import get_current_user
from pydantic import BaseModel
import bcrypt

router = APIRouter()

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(database.get_db)):
    # Check if user already exists
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")

    # Hash the password
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    new_user = models.User(username=user.username, email=user.email, hashed_password=hashed_password.decode('utf-8'))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"msg": "User created successfully"}

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(database.get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if not db_user or not bcrypt.checkpw(user.password.encode('utf-8'), db_user.hashed_password.encode('utf-8')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Create JWT token
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/protected")
def protected_route(user: str = Depends(get_current_user)):
    return {"message": f"Hello, {user}. You have access!"}