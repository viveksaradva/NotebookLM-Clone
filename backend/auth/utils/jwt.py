from datetime import datetime, timedelta
from typing import Optional 
from jose import jwt, JWTError
from dotenv import load_dotenv
import os

load_dotenv()

# Secret and algorithm config
SECRET_KEY = os.getenv("SECRET_KEY")  
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Generates a JWT token with expiration.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str) -> dict:
    """
    Validates a JWT token.
    Returns payload if valid.
    Raises JWTError if invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise JWTError(f"Token validation failed: {str(e)}")
