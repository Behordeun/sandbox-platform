from app.core.database import Base
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func


class TokenBlacklist(Base):
    __tablename__ = "token_blacklist"

    id = Column(Integer, primary_key=True, index=True)
    jti = Column(String(255), unique=True, index=True, nullable=False)  # JWT ID
    token_type = Column(String(50), nullable=False)  # access or refresh
    user_id = Column(Integer, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    blacklisted_at = Column(DateTime(timezone=True), server_default=func.now())
    reason = Column(String(255), nullable=True)  # logout, revoked, etc.