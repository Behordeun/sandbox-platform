import secrets
from datetime import datetime, timedelta
from typing import Optional

from app.core.security import create_access_token, create_refresh_token
from app.crud.base import CRUDBase
from app.models.oauth_token import OAuthToken
from app.schemas.oauth import TokenRequest, TokenResponse
from sqlalchemy.orm import Session


class CRUDOAuthToken(CRUDBase[OAuthToken, TokenRequest, TokenResponse]):
    def get_by_access_token(
        self, db: Session, *, access_token: str
    ) -> Optional[OAuthToken]:
        q = db.query(OAuthToken).filter(OAuthToken.access_token == access_token)
        if hasattr(OAuthToken, "is_deleted"):
            q = q.filter(OAuthToken.is_deleted == False)  # noqa: E712
        return q.first()

    def get_by_refresh_token(
        self, db: Session, *, refresh_token: str
    ) -> Optional[OAuthToken]:
        q = db.query(OAuthToken).filter(OAuthToken.refresh_token == refresh_token)
        if hasattr(OAuthToken, "is_deleted"):
            q = q.filter(OAuthToken.is_deleted == False)  # noqa: E712
        return q.first()

    def get_by_authorization_code(
        self, db: Session, *, code: str
    ) -> Optional[OAuthToken]:
        q = db.query(OAuthToken).filter(
            OAuthToken.authorization_code == code,
            OAuthToken.code_expires_at > datetime.now(),
        )
        if hasattr(OAuthToken, "is_deleted"):
            q = q.filter(OAuthToken.is_deleted == False)  # noqa: E712
        return q.first()

    def create_authorization_code(
        self,
        db: Session,
        *,
        user_id: int,
        client_id: str,
        scope: Optional[str] = None,
        expires_in: int = 600  # 10 minutes
    ) -> OAuthToken:
        """Create authorization code for OAuth2 flow."""
        code = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(seconds=expires_in)

        db_obj = OAuthToken(
            authorization_code=code,
            code_expires_at=expires_at,
            user_id=user_id,
            client_id=client_id,
            scope=scope,
            access_token="",  # Will be set when exchanged
            expires_at=expires_at,  # Temporary, will be updated
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def exchange_code_for_tokens(
        self,
        db: Session,
        *,
        code: str,
        client_id: str,
        access_token_expires_in: int = 3600,  # 1 hour
        refresh_token_expires_in: int = 604800  # 7 days
    ) -> Optional[OAuthToken]:
        """Exchange authorization code for access and refresh tokens."""
        token_obj = self.get_by_authorization_code(db, code=code)
        if token_obj is None:
            return None
        if getattr(token_obj, "client_id", None) != client_id:
            return None

        # Generate new tokens
        access_token = create_access_token(subject=token_obj.user_id)
        refresh_token = create_refresh_token(subject=token_obj.user_id)

        # Update token object
        setattr(token_obj, "access_token", access_token)
        setattr(token_obj, "refresh_token", refresh_token)
        setattr(
            token_obj,
            "expires_at",
            datetime.now() + timedelta(seconds=access_token_expires_in),
        )
        setattr(token_obj, "authorization_code", None)  # Clear the code
        setattr(token_obj, "code_expires_at", None)

        db.add(token_obj)
        db.commit()
        db.refresh(token_obj)
        return token_obj

    def create_client_credentials_token(
        self,
        db: Session,
        *,
        client_id: str,
        scope: Optional[str] = None,
        expires_in: int = 3600
    ) -> OAuthToken:
        """Create token for client credentials grant."""
        access_token = create_access_token(subject=client_id)
        expires_at = datetime.now() + timedelta(seconds=expires_in)

        db_obj = OAuthToken(
            access_token=access_token,
            token_type="Bearer",
            scope=scope,
            expires_at=expires_at,
            user_id=None,  # No user for client credentials
            client_id=client_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def refresh_access_token(
        self, db: Session, *, refresh_token: str, expires_in: int = 3600
    ) -> Optional[OAuthToken]:
        """Refresh access token using refresh token."""
        token_obj = self.get_by_refresh_token(db, refresh_token=refresh_token)
        if not token_obj:
            return None

        # Generate new access token
        access_token = create_access_token(subject=token_obj.user_id)

        # Update token object
        setattr(token_obj, "access_token", access_token)
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        token_obj.__setattr__("expires_at", expires_at)

        db.add(token_obj)
        db.commit()
        db.refresh(token_obj)
        return token_obj

    def is_token_valid(self, db: Session, *, access_token: str) -> bool:
        """Check if access token is valid and not expired."""
        token_obj = self.get_by_access_token(db, access_token=access_token)
        if not token_obj:
            return False
        expires_at = getattr(token_obj, "expires_at", None)
        if expires_at is None:
            return False
        return bool(expires_at > datetime.now())

    def revoke_token(self, db: Session, *, access_token: str) -> bool:
        """Revoke access token."""
        token_obj = self.get_by_access_token(db, access_token=access_token)
        if not token_obj:
            return False

        # Soft delete token (preserve row for audit)
        try:
            if hasattr(token_obj, "is_deleted"):
                from datetime import datetime

                setattr(token_obj, "is_deleted", True)
                if hasattr(token_obj, "deleted_at"):
                    setattr(token_obj, "deleted_at", datetime.now())
                db.add(token_obj)
                db.commit()
                db.refresh(token_obj)
                return True
        except Exception:
            pass
        # Fallback to hard delete if soft-delete not available
        db.delete(token_obj)
        db.commit()
        return True


oauth_token_crud = CRUDOAuthToken(OAuthToken)
