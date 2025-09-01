from datetime import timedelta
from typing import Any

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.crud.user import user_crud
from app.dependencies.auth import get_current_active_user
from app.dependencies.database import get_db
from app.schemas.oauth import TokenResponse
from app.schemas.user import UserLogin, UserResponse
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login_user(
    request: Request,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    🔐 OAuth2 Compatible Login

    Authenticate user with form data and return JWT tokens.
    Compatible with OAuth2 password flow for API clients.

    **Request Format:**
    - Content-Type: application/x-www-form-urlencoded
    - username: Email or username
    - password: User password

    **Response:**
    - access_token: JWT token for API access
    - refresh_token: Token for refreshing access
    - token_type: "bearer"
    - expires_in: Token expiration in seconds

    **Use Cases:**
    - OAuth2 client applications
    - API integrations requiring form-based auth
    - Third-party service authentication
    """
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

    # Expose user context for middleware logging
    try:
        request.state.user_id = user.id
    except Exception:
        pass

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
    request: Request,
    db: Session = Depends(get_db),
    user_in: UserLogin,
) -> Any:
    """
    🚀 JSON Login for Nigerian Startups

    Primary login endpoint for Nigerian DPI developers.
    Accepts JSON payload with email or username authentication.

    **Request Example:**
    ```json
    {
        "identifier": "adebayo@fintech.ng",  // Email or username
        "password": "SecurePass123"
    }
    ```

    **Features:**
    - ✅ Email or username login
    - ✅ JWT token generation
    - ✅ Last login tracking
    - ✅ Request correlation ID support

    **Nigerian Context:**
    - Supports Nigerian email domains (.ng, .com.ng)
    - Optimized for fintech and DPI applications
    - Audit logging for regulatory compliance
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

    # Expose user context for middleware logging
    try:
        request.state.user_id = user.id
    except Exception:
        pass

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
    """
    👤 Get Current User Profile

    Retrieve authenticated user's profile information.
    Requires valid JWT token in Authorization header.

    **Headers Required:**
    - Authorization: Bearer {access_token}

    **Returns:**
    - User profile with Nigerian DPI context
    - NIN/BVN verification status
    - Account activity information

    **Security:**
    - Token validation required
    - Active user status check
    - Soft-delete filtering applied
    """
    return current_user


@router.post("/logout")
def logout_user() -> Any:
    """
    🚪 User Logout

    Logout current user session.
    Client should remove tokens from storage.

    **Process:**
    1. Client receives logout confirmation
    2. Client removes access/refresh tokens
    3. Tokens become invalid on next request

    **Best Practice:**
    - Clear all stored authentication data
    - Redirect to login page
    - Invalidate any cached user data

    **Note:** Server-side token blacklisting available
    for enhanced security in production.
    """
    return {"message": "Successfully logged out"}
