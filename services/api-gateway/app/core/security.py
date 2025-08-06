from typing import Optional
from jose import jwt, JWTError
from fastapi import HTTPException, status
from .config import settings


def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(
            token, 
            settings.jwt_secret_key, 
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except JWTError:
        return None


def extract_user_id_from_token(token: str) -> Optional[str]:
    """Extract user ID from JWT token."""
    payload = verify_token(token)
    if payload:
        return payload.get("sub")
    return None


def validate_api_key(api_key: str) -> bool:
    """Validate API key (placeholder implementation)."""
    # In a real implementation, this would check against a database
    # or external service
    return api_key.startswith("sk-") and len(api_key) > 20


class SecurityError(Exception):
    """Custom security exception."""
    pass


def create_auth_exception(detail: str = "Could not validate credentials") -> HTTPException:
    """Create authentication exception."""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )

