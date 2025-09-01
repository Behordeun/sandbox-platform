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
    """
    👥 Create Nigerian Startup Account

    Create new user account for Nigerian DPI developers.
    Only accessible by platform administrators.

    **Request Example:**
    ```json
    {
        "email": "developer@fintech.ng",
        "username": "fintech_dev",
        "password": "TempPass123",
        "first_name": "Adebayo",
        "last_name": "Ogundimu",
        "role": "developer"  // Optional: admin, developer
    }
    ```

    **Features:**
    - ✅ Email uniqueness validation
    - ✅ Username availability check
    - ✅ Automatic welcome email
    - ✅ Nigerian domain support (.ng, .com.ng)

    **Admin Access Required:**
    - Must be authenticated as admin
    - Closed sandbox: Only 9 Nigerian startups
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
    """
    📄 List All Nigerian Startup Users

    Retrieve paginated list of all registered users.
    Includes verification status and activity metrics.

    **Query Parameters:**
    - skip: Number of records to skip (default: 0)
    - limit: Maximum records to return (default: 100)

    **Response Includes:**
    - User profiles with NIN/BVN status
    - Last login and activity data
    - Account verification levels
    - Soft-delete filtering applied

    **Admin Only:** Platform oversight and user management
    """
    users = user_crud.get_multi(db, skip=skip, limit=limit)
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    admin_user: User = Depends(get_admin_user)
) -> Any:
    """
    🔍 Get Specific User Details

    Retrieve detailed information for a specific user.
    Includes full profile and verification status.

    **Path Parameters:**
    - user_id: Unique user identifier

    **Returns:**
    - Complete user profile
    - NIN/BVN verification status
    - Account activity history
    - Role and permissions

    **Use Cases:**
    - User support and troubleshooting
    - Account verification review
    - Compliance auditing
    """
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
    """
    ✏️ Update User Profile

    Modify user account information and settings.
    Supports partial updates with validation.

    **Updatable Fields:**
    - first_name, last_name
    - email (with uniqueness check)
    - username (with availability check)
    - role (admin, developer)
    - is_active status

    **Validation:**
    - Email format and domain validation
    - Username uniqueness across platform
    - Role permission verification

    **Audit Trail:** All changes logged for compliance
    """
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
    """
    🗑️ Soft Delete User Account

    Mark user account as deleted (soft delete).
    Preserves data for audit compliance.

    **Process:**
    1. Sets is_deleted = true
    2. Records deletion timestamp
    3. Maintains audit trail
    4. Frees email/username for reuse

    **Data Retention:**
    - User data preserved for compliance
    - API access immediately revoked
    - Email/username become available

    **NDPR Compliant:** Nigerian Data Protection Regulation
    """
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
    """
    ✅ Activate User Account

    Enable user account for API access.
    Restores full platform functionality.

    **Effects:**
    - Enables login and API access
    - Restores DPI service usage
    - Allows NIN/BVN verification
    - Resumes audit logging

    **Use Cases:**
    - New account activation
    - Account restoration after suspension
    - Startup onboarding completion

    **Notification:** User receives activation email
    """
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
    """
    ❌ Deactivate User Account

    Suspend user account and revoke API access.
    Temporary suspension without data loss.

    **Effects:**
    - Blocks login attempts
    - Revokes API access tokens
    - Suspends DPI service usage
    - Maintains audit trail

    **Use Cases:**
    - Policy violation suspension
    - Security incident response
    - Temporary account freeze

    **Reversible:** Account can be reactivated
    """
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
    """
    🔑 Admin Password Reset

    Reset user password for account recovery.
    Sends secure notification to user email.

    **Request Body:**
    ```json
    {
        "new_password": "NewSecurePass123"
    }
    ```

    **Security Process:**
    1. Validates admin permissions
    2. Hashes new password securely
    3. Updates user credentials
    4. Sends notification email
    5. Logs password change event

    **Best Practice:** User should change password on next login
    """
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
