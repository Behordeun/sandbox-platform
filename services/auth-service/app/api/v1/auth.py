from datetime import timedelta
from typing import Any

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.crud.user import user_crud
from app.dependencies.auth import get_current_active_user
from app.dependencies.database import get_db
from app.schemas.oauth import TokenResponse
from app.schemas.user import UserLogin, UserResponse
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login_user(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login, get an access token for future requests."""
    user = user_crud.authenticate(
        db, identifier=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
        )
    elif not user_crud.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    # Update last login
    user_crud.update_last_login(db, user=user)

    # Create tokens
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(subject=user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.jwt_access_token_expire_minutes * 60,
    }


@router.post("/login/json", response_model=TokenResponse)
def login_user_json(
    *,
    db: Session = Depends(get_db),
    user_in: UserLogin,
) -> Any:
    """Login with JSON payload using email or username.

    Example:
    {
        "identifier": "adebayo@fintech.ng",  // or "adebayo_dev"
        "password": "SecurePass123"
    }
    """
    user = user_crud.authenticate(
        db, identifier=user_in.identifier, password=user_in.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
        )
    elif not user_crud.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    # Update last login
    user_crud.update_last_login(db, user=user)

    # Create tokens
    access_token_expires = timedelta(minutes=settings.jwt_access_token_expire_minutes)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(subject=user.id)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.jwt_access_token_expire_minutes * 60,
    }


@router.get("/me", response_model=UserResponse)
def read_user_me(
    current_user: UserResponse = Depends(get_current_active_user),
) -> Any:
    """Get current user."""
    return current_user


@router.post("/logout")
def logout_user() -> Any:
    """Logout user (client-side token removal)."""
    return {"message": "Successfully logged out"}
