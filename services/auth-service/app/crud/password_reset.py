import secrets
from datetime import datetime, timedelta
from typing import Optional

from app.crud.base import CRUDBase
from app.models.password_reset import PasswordResetToken
from sqlalchemy.orm import Session


class CRUDPasswordReset(CRUDBase[PasswordResetToken, dict, dict]):
    def create_reset_token(
        self, db: Session, *, email: str, expires_in_minutes: int = 30
    ) -> PasswordResetToken:
        """Create a password reset token."""
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(minutes=expires_in_minutes)
        
        db_obj = PasswordResetToken(
            email=email,
            token=token,
            expires_at=expires_at
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_token(self, db: Session, *, token: str) -> Optional[PasswordResetToken]:
        """Get reset token by token string."""
        return db.query(PasswordResetToken).filter(
            PasswordResetToken.token == token,
            PasswordResetToken.expires_at > datetime.now(),
            PasswordResetToken.is_used == False
        ).first()

    def mark_as_used(self, db: Session, *, token_obj: PasswordResetToken) -> PasswordResetToken:
        """Mark token as used."""
        token_obj.is_used = True
        db.add(token_obj)
        db.commit()
        db.refresh(token_obj)
        return token_obj

    def cleanup_expired_tokens(self, db: Session) -> int:
        """Remove expired tokens."""
        count = db.query(PasswordResetToken).filter(
            PasswordResetToken.expires_at < datetime.now()
        ).delete()
        db.commit()
        return count


password_reset_crud = CRUDPasswordReset(PasswordResetToken)