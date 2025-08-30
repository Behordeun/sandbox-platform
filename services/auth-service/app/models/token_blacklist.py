from app.core.database import Base
from app.models.mixins import SoftDeleteMixin
from app.core.yaml_config import settings
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class TokenBlacklist(Base, SoftDeleteMixin):
    __tablename__ = f"{settings.table_prefix}token_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(255), unique=True, index=True, nullable=False)  # JWT ID
    token_type = Column(String(50), nullable=False)  # access or refresh
    # Link to users table (prefixed in this service)
    user_id = Column(
        Integer, ForeignKey(f"{settings.table_prefix}users.id"), nullable=False
    )
    expires_at = Column(DateTime(timezone=True), nullable=False)
    blacklisted_at = Column(DateTime(timezone=True), server_default=func.now())
    reason = Column(String(255), nullable=True)  # logout, revoked, etc.

    # Relationship to user
    user = relationship("User", backref="blacklisted_tokens")
