"""
Admin endpoints for user management
Only accessible by sandbox administrators
"""

USER_NOT_FOUND_MSG = "User not found"

from typing import Any, List

from app.crud.user import user_crud
from app.dependencies.auth import get_current_active_user
from app.dependencies.database import get_db
from app.email_service import email_service
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter()


def get_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """Verify current user is an admin (role-based, fallback to email for legacy admins)."""
    # Role-based check (preferred)
    if getattr(current_user, "role", None) == "admin":
        return current_user

    # Fallback: check if user email contains 'admin' or is in admin list
    admin_emails = [
        "admin@dpi-sandbox.ng",
        "muhammad@datasciencenigeria.ai",
    ]
    if (
        current_user.email not in admin_emails
        and "admin" not in current_user.email.lower()
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )
    return current_user


@router.post("/users", response_model=UserResponse)
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    admin_user: User = Depends(get_admin_user)
) -> Any:
    """Create a new user account (Admin only).

    Example:
    {
        "email": "developer@fintech.ng",
        "username": "fintech_dev",
        "password": "TempPass123",
        "first_name": "John",
        "last_name": "Doe"
    }
    """
    # Check if user already exists
    user = user_crud.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400, detail="User with this email already exists"
        )

    # Check username if provided
    if user_in.username:
        existing_user = user_crud.get_by_username(db, username=user_in.username)
        if existing_user:
            raise HTTPException(
                status_code=400, detail="User with this username already exists"
            )

    # Create user (role can be specified in payload)
    user = user_crud.create(db, obj_in=user_in)

    # Send welcome email with credentials
    email_service.send_account_created_notification(
        to_email=user.email,
        first_name=user.first_name or "Developer",
        username=user.username or user.email,
        temporary_password=user_in.password,
    )

    return user


@router.get("/users", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_admin_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """List all users (Admin only)."""
    users = user_crud.get_multi(db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    admin_user: User = Depends(get_admin_user)
) -> Any:
    """Get user by ID (Admin only)."""
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND_MSG)
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
    admin_user: User = Depends(get_admin_user)
) -> Any:
    """Update user (Admin only)."""
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND_MSG)

    user = user_crud.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/users/{user_id}")
def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    admin_user: User = Depends(get_admin_user)
) -> Any:
    """Delete user (Admin only)."""
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND_MSG)

    user_crud.remove(db, id=user_id)
    return {"message": "User deleted successfully"}


@router.post("/users/{user_id}/activate")
def activate_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    admin_user: User = Depends(get_admin_user)
) -> Any:
    """Activate user (Admin only)."""
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND_MSG)

    user.is_active = True
    db.add(user)
    db.commit()

    return {"message": "User activated successfully"}


@router.post("/users/{user_id}/deactivate")
def deactivate_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    admin_user: User = Depends(get_admin_user)
) -> Any:
    """Deactivate user (Admin only)."""
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND_MSG)

    user.is_active = False
    db.add(user)
    db.commit()

    return {"message": "User deactivated successfully"}


@router.post("/users/{user_id}/reset-password")
def reset_user_password(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    new_password: str,
    admin_user: User = Depends(get_admin_user)
) -> Any:
    """Reset user password (Admin only)."""
    from app.core.security import get_password_hash
    
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail=USER_NOT_FOUND_MSG)

    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    db.commit()

    # Send password reset notification
    email_service.send_password_reset_notification(
        to_email=user.email,
        first_name=user.first_name or "Developer",
        new_password=new_password,
    )

    return {"message": "Password reset successfully"}
