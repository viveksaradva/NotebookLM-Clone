from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from backend.auth.utils.jwt import verify_access_token

# Use the login endpoint as the OAuth2 password flow URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """
    Dependency to extract the current user from JWT token.
    Raises HTTPException if token is invalid or user not found.
    """
    try:
        payload = verify_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject (sub)",
            )
        return username

    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
        )
