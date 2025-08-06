from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Any
from datetime import timedelta

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_active_user
from app.crud.user import user_crud
from app.schemas.user import UserCreate, UserResponse, UserLogin, UserProfile
from app.schemas.oauth import TokenResponse
from app.core.security import create_access_token, create_refresh_token
from app.core.config import settings

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """Register a new user."""
    # Check if user already exists
    user = user_crud.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    # Check username if provided
    if user_in.username:
        existing_user = user_crud.get_by_username(db, username=user_in.username)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="The user with this username already exists in the system.",
            )
    
    # Create user
    user = user_crud.create(db, obj_in=user_in)
    return user


@router.post("/login", response_model=TokenResponse)
def login_user(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login, get an access token for future requests."""
    user = user_crud.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    elif not user_crud.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
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
    """Login with JSON payload."""
    user = user_crud.authenticate(
        db, email=user_in.email, password=user_in.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    elif not user_crud.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
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


@router.get("/userinfo", response_model=UserProfile)
def get_user_info(
    current_user: UserResponse = Depends(get_current_active_user)
) -> Any:
    """Get current user information."""
    return current_user


@router.get("/me", response_model=UserResponse)
def read_user_me(
    current_user: UserResponse = Depends(get_current_active_user),
) -> Any:
    """Get current user."""
    return current_user

