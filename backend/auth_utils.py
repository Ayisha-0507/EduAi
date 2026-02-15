"""
EduAI Backend — JWT Auth Utilities
"""

from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import settings

security = HTTPBearer()


def create_jwt(uid: str, email: str) -> str:
    """Create a JWT token for authenticated users."""
    payload = {
        "uid": uid,
        "email": email,
        "exp": datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def verify_jwt(token: str) -> dict:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


async def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """FastAPI dependency: extract the current user from the Authorization header."""
    return verify_jwt(creds.credentials)
