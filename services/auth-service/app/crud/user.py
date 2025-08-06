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
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        return user.is_active

    def verify_nin(
        self, db: Session, *, user: User, nin: str, verification_data: dict = None
    ) -> User:
        """Verify and store NIN for user."""
        # Hash the NIN for privacy
        nin_hash = hashlib.sha256(nin.encode()).hexdigest()
        user.nin_hash = nin_hash
        user.nin_verified = True

        # Store verification data if provided
        if verification_data:
            profile_data = json.loads(user.profile_data) if user.profile_data else {}
            profile_data["nin_verification"] = verification_data
            user.profile_data = json.dumps(profile_data)

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def verify_bvn(
        self, db: Session, *, user: User, bvn: str, verification_data: dict = None
    ) -> User:
        """Verify and store BVN for user."""
        # Hash the BVN for privacy
        bvn_hash = hashlib.sha256(bvn.encode()).hexdigest()
        user.bvn_hash = bvn_hash
        user.bvn_verified = True

        # Store verification data if provided
        if verification_data:
            profile_data = json.loads(user.profile_data) if user.profile_data else {}
            profile_data["bvn_verification"] = verification_data
            user.profile_data = json.dumps(profile_data)

        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update_last_login(self, db: Session, *, user: User) -> User:
        """Update user's last login timestamp."""
        from datetime import datetime

        user.last_login = datetime.utcnow()
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


user_crud = CRUDUser(User)
