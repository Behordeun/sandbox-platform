from app.core.security import verify_token
from app.crud.user import user_crud
from app.dependencies.database import get_db
from app.models.user import User
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

# OAuth2 scheme for token authentication
oauth2_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        user_id = verify_token(token, token_type="access")
        if user_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    user = user_crud.get(db, id=int(user_id))
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user."""
    if not user_crud.is_active(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


async def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    """Get current user if token is provided and valid, otherwise return None."""
    if not credentials:
        return None

    try:
        token = credentials.credentials
        user_id = verify_token(token, token_type="access")
        if user_id is None:
            return None

        user = user_crud.get(db, id=int(user_id))
        return user
    except Exception:
        return None
