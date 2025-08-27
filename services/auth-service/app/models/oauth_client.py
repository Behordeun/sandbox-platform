from app.core.database import Base
from app.core.yaml_config import settings
from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func


class OAuthClient(Base):
    __tablename__ = f"{settings.table_prefix}oauth_clients"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String(255), unique=True, index=True, nullable=False)
    client_secret = Column(String(255), nullable=False)

    # Client information
    client_name = Column(String(255), nullable=False)
    client_description = Column(Text, nullable=True)
    client_uri = Column(String(500), nullable=True)

    # OAuth2 configuration
    grant_types = Column(
        JSON, nullable=False, default=["authorization_code", "refresh_token"]
    )
    response_types = Column(JSON, nullable=False, default=["code"])
    redirect_uris = Column(JSON, nullable=False)
    scope = Column(String(500), nullable=False, default="openid profile email")

    # Client status
    is_active = Column(Boolean, default=True)
    is_confidential = Column(
        Boolean, default=True
    )  # True for server-side apps, False for public clients

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Additional client metadata
    client_metadata = Column(JSON, nullable=True)
