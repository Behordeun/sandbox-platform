from app.core.security import verify_token
from fastapi import Request
from app.core.system_logger import system_logger
from app.crud.user import user_crud
from app.dependencies.database import get_db
from app.models.user import User
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

# OAuth2 scheme for token authentication
oauth2_scheme = HTTPBearer()


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user from JWT token."""
    from app.crud.token_blacklist import token_blacklist_crud

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = verify_token(token, token_type="access")
        if payload is None:
            raise credentials_exception

        # Check if token is blacklisted
        jti = payload.get("jti")
        if jti and token_blacklist_crud.is_token_blacklisted(db, jti=jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except HTTPException as http_exc:
        system_logger.warning(
            "Credential validation failed",
            {"reason": http_exc.detail, "stage": "token_validation"},
        )
        raise
    except Exception as e:
        system_logger.error(e, {"stage": "token_validation"}, exc_info=True)
        raise credentials_exception

    # Persist user context on the request for downstream middlewares/handlers
    try:
        request.state.user_id = int(user_id)
    except Exception:
        pass

    user = user_crud.get(db, id=int(user_id))
    if user is None:
        system_logger.warning(
            "Authenticated user not found",
            {"stage": "load_user", "user_id": user_id},
        )
        raise credentials_exception

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user."""
    if not user_crud.is_active(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User | None:
    """Get current user if token is provided and valid, otherwise return None."""
    if not credentials:
        return None

    try:
        token = credentials.credentials
        payload = verify_token(token, token_type="access")
        if payload is None:
            return None
        user_id = payload.get("sub")
        if not user_id:
            return None
        user = user_crud.get(db, id=int(user_id))
        return user
    except Exception:
        return None
