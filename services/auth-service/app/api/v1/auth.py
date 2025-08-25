from datetime import timedelta
from typing import Any

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.crud.user import user_crud
from app.dependencies.auth import get_current_active_user, oauth2_scheme
from app.dependencies.database import get_db
from app.models.user import User
from app.schemas.oauth import TokenResponse
from app.schemas.user import UserCreate, UserLogin, UserProfile, UserResponse
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

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
    """Login with JSON payload using email or username."""
    user = user_crud.authenticate(db, identifier=user_in.identifier, password=user_in.password)
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


@router.get("/userinfo", response_model=UserProfile)
def get_user_info(current_user: UserResponse = Depends(get_current_active_user)) -> Any:
    """Get current user information."""
    return current_user


@router.get("/me", response_model=UserResponse)
def read_user_me(
    current_user: UserResponse = Depends(get_current_active_user),
) -> Any:
    """Get current user."""
    return current_user


@router.post("/logout")
def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Any:
    """Logout user by blacklisting current token."""
    from app.crud.token_blacklist import token_blacklist_crud
    from app.core.security import verify_token
    from datetime import datetime
    
    try:
        token = credentials.credentials
        payload = verify_token(token, token_type="access")
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
            
        # Blacklist the token
        token_blacklist_crud.blacklist_token(
            db,
            jti=payload["jti"],
            token_type="access",
            user_id=int(payload["sub"]),
            expires_at=datetime.fromtimestamp(payload["exp"]),
            reason="logout"
        )
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Logout failed"
        )


@router.post("/revoke-token")
def revoke_token(
    token_jti: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Revoke a specific token by JTI (admin function)."""
    from app.crud.token_blacklist import token_blacklist_crud
    from datetime import datetime, timedelta
    
    # For now, allow users to revoke their own tokens
    # In production, add admin role check
    
    token_blacklist_crud.blacklist_token(
        db,
        jti=token_jti,
        token_type="access",  # Could be made dynamic
        user_id=current_user.id,
        expires_at=datetime.now() + timedelta(days=1),  # Default expiry
        reason="manual_revocation"
    )
    
    return {"message": "Token revoked successfully"}
