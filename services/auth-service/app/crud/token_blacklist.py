from datetime import datetime
from typing import Optional

from app.crud.base import CRUDBase
from app.models.token_blacklist import TokenBlacklist
from sqlalchemy.orm import Session


class CRUDTokenBlacklist(CRUDBase[TokenBlacklist, dict, dict]):
    def is_token_blacklisted(self, db: Session, *, jti: str) -> bool:
        """Check if token is blacklisted."""
        q = db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti)
        if hasattr(TokenBlacklist, "is_deleted"):
            q = q.filter(TokenBlacklist.is_deleted == False)  # noqa: E712
        token = q.first()
        return token is not None

    def blacklist_token(
        self,
        db: Session,
        *,
        jti: str,
        token_type: str,
        user_id: int,
        expires_at: datetime,
        reason: Optional[str] = None
    ) -> TokenBlacklist:
        """Add token to blacklist."""
        db_obj = TokenBlacklist(
            jti=jti,
            token_type=token_type,
            user_id=user_id,
            expires_at=expires_at,
            reason=reason,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def cleanup_expired_tokens(self, db: Session) -> int:
        """Remove expired tokens from blacklist."""
        # Soft-delete expired tokens to avoid hard deletes in dev
        q = db.query(TokenBlacklist).filter(TokenBlacklist.expires_at < datetime.now())
        if hasattr(TokenBlacklist, "is_deleted"):
            from datetime import datetime

            updated = 0
            for tok in q.all():
                if getattr(tok, "is_deleted", False):
                    continue
                setattr(tok, "is_deleted", True)
                if hasattr(tok, "deleted_at"):
                    setattr(tok, "deleted_at", datetime.now())
                db.add(tok)
                updated += 1
            db.commit()
            return updated
        # Fallback hard delete if soft-delete not available
        count = q.delete()
        db.commit()
        return count


token_blacklist_crud = CRUDTokenBlacklist(TokenBlacklist)
