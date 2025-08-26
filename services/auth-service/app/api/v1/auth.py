from datetime import timedelta
from typing import Any

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
)
from app.crud.password_reset import password_reset_crud
from app.crud.user import user_crud
from app.dependencies.auth import get_current_active_user, oauth2_scheme
from app.dependencies.database import get_db
from app.email_service import email_service
from app.models.user import User
from app.schemas.oauth import TokenResponse
from app.schemas.password_reset import (
    PasswordResetConfirm,
    PasswordResetRequest,
    PasswordResetResponse,
)
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
    """Register a new user.

    Example for Nigerian DPI developers:
    {
        "email": "adebayo@fintech.ng",
        "username": "adebayo_dev",
        "password": "SecurePass123",
        "first_name": "Adebayo",
        "last_name": "Ogundimu",
        "phone_number": "+2348012345678"
    }
    """
    # Check if user already exists
    user = user_crud.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail={
                "success": False,
                "message": "Email already registered",
                "error_code": "EMAIL_EXISTS",
                "details": {
                    "suggestion": "Try logging in or use password reset if you forgot your password",
                    "login_url": "/api/v1/auth/login",
                    "reset_url": "/api/v1/auth/password-reset/request",
                },
            },
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

    # Send registration confirmation email
    email_service.send_registration_confirmation(
        to_email=user.email, first_name=user.first_name or "Developer"
    )

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
    from datetime import datetime

    from app.core.security import verify_token
    from app.crud.token_blacklist import token_blacklist_crud

    try:
        token = credentials.credentials
        payload = verify_token(token, token_type="access")
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        # Blacklist the token
        token_blacklist_crud.blacklist_token(
            db,
            jti=payload["jti"],
            token_type="access",
            user_id=int(payload["sub"]),
            expires_at=datetime.fromtimestamp(payload["exp"]),
            reason="logout",
        )

        return {"message": "Successfully logged out"}

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Logout failed"
        )


@router.post("/revoke-token")
def revoke_token(
    token_jti: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Any:
    """Revoke a specific token by JTI (admin function)."""
    from datetime import datetime, timedelta

    from app.crud.token_blacklist import token_blacklist_crud

    # For now, allow users to revoke their own tokens
    # In production, add admin role check

    token_blacklist_crud.blacklist_token(
        db,
        jti=token_jti,
        token_type="access",  # Could be made dynamic
        user_id=current_user.id,
        expires_at=datetime.now() + timedelta(days=1),  # Default expiry
        reason="manual_revocation",
    )

    return {"message": "Token revoked successfully"}


@router.post("/password-reset/request", response_model=PasswordResetResponse)
def request_password_reset(
    *,
    db: Session = Depends(get_db),
    reset_request: PasswordResetRequest,
) -> Any:
    """Request password reset token."""
    user = user_crud.get_by_email(db, email=reset_request.email)
    if not user:
        # Don't reveal if email exists for security
        return {"message": "If the email exists, a reset link has been sent"}

    # Create reset token
    token_obj = password_reset_crud.create_reset_token(db, email=reset_request.email)

    # Send password reset email with verification link
    email_sent = email_service.send_password_reset_email(
        to_email=reset_request.email, reset_token=token_obj.token
    )

    if email_sent:
        return {"message": "Password reset link sent to your email"}
    else:
        return {
            "message": f"Reset token: {token_obj.token}"
        }  # Fallback for development


@router.post("/password-reset/confirm", response_model=PasswordResetResponse)
def confirm_password_reset(
    *,
    db: Session = Depends(get_db),
    reset_confirm: PasswordResetConfirm,
) -> Any:
    """Confirm password reset with token."""
    # Validate token
    token_obj = password_reset_crud.get_by_token(db, token=reset_confirm.token)
    if not token_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Get user
    user = user_crud.get_by_email(db, email=token_obj.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Update password
    user.hashed_password = get_password_hash(reset_confirm.new_password)
    db.add(user)

    # Mark token as used
    password_reset_crud.mark_as_used(db, token_obj=token_obj)

    db.commit()

    return {"message": "Password reset successfully"}


@router.get("/password-reset/verify")
def verify_reset_token(
    token: str,
    email: str,
    db: Session = Depends(get_db),
) -> Any:
    """Verify password reset token from email link."""
    # Validate token
    token_obj = password_reset_crud.get_by_token(db, token=token)
    if not token_obj or token_obj.email != email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    return {"message": "Token verified successfully", "email": email, "token": token}
