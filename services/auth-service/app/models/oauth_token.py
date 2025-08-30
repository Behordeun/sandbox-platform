from app.core.database import Base
from app.models.mixins import SoftDeleteMixin
from app.core.yaml_config import settings
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class OAuthToken(Base, SoftDeleteMixin):
    __tablename__ = f"{settings.table_prefix}oauth_tokens"

    id = Column(Integer, primary_key=True, index=True)

    # Token information
    access_token = Column(String(500), unique=True, index=True, nullable=False)
    refresh_token = Column(String(500), unique=True, index=True, nullable=True)
    token_type = Column(String(50), default="Bearer")

    # Token metadata
    scope = Column(String(500), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    # Relationships (respect service table prefix)
    user_id = Column(
        Integer, ForeignKey(f"{settings.table_prefix}users.id"), nullable=False
    )
    client_id = Column(
        String(255),
        ForeignKey(f"{settings.table_prefix}oauth_clients.client_id"),
        nullable=False,
    )

    # Authorization code (temporary)
    authorization_code = Column(String(255), nullable=True)
    code_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Additional token data
    token_data = Column(Text, nullable=True)  # Store as JSON string

    # Relationships
    user = relationship("User", backref="oauth_tokens")
    client = relationship("OAuthClient", backref="oauth_tokens")
