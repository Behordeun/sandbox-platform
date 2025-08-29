import hashlib
import json
from typing import Optional

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from sqlalchemy.orm import Session


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            first_name=obj_in.first_name,
            last_name=obj_in.last_name,
            phone_number=obj_in.phone_number,
            role=getattr(obj_in, "role", "user"),  # Set role if provided
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(
        self, db: Session, *, identifier: str, password: str
    ) -> Optional[User]:
        # Try to find user by email first, then by username
        user = self.get_by_email(db, email=identifier)
        if not user:
            user = self.get_by_username(db, username=identifier)

        if not user:
            return None

        hashed_password = getattr(user, "hashed_password", None)
        if not isinstance(hashed_password, str) or not verify_password(
            password, hashed_password
        ):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return bool(user.is_active)

    def verify_nin(
        self,
        db: Session,
        *,
        user: User,
        nin: str,
        verification_data: Optional[dict] = None
    ) -> User:
        """Verify and store NIN for user."""
        # Hash the NIN for privacy
        nin_hash = hashlib.sha256(nin.encode()).hexdigest()
        setattr(user, "nin_hash", nin_hash)
        setattr(user, "nin_verified", True)

        # Store verification data if provided
        if verification_data:
            profile_data_value = getattr(user, "profile_data", None)
            profile_data = json.loads(profile_data_value) if profile_data_value else {}
            profile_data["nin_verification"] = verification_data
            setattr(user, "profile_data", json.dumps(profile_data))

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def verify_bvn(
        self,
        db: Session,
        *,
        user: User,
        bvn: str,
        verification_data: Optional[dict] = None
    ) -> User:
        """Verify and store BVN for user."""
        # Hash the BVN for privacy
        bvn_hash = hashlib.sha256(bvn.encode()).hexdigest()
        setattr(user, "bvn_hash", bvn_hash)
        setattr(user, "bvn_verified", True)

        # Store verification data if provided
        if verification_data:
            profile_data_value = getattr(user, "profile_data", None)
            profile_data = json.loads(profile_data_value) if profile_data_value else {}
            profile_data["bvn_verification"] = verification_data
            setattr(user, "profile_data", json.dumps(profile_data))

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update_last_login(self, db: Session, *, user: User) -> User:
        """Update user's last login timestamp."""
        from datetime import datetime

        # Ensure we set the value, not the Column object
        if hasattr(user, "last_login"):
            setattr(user, "last_login", datetime.now())
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


user_crud = CRUDUser(User)
