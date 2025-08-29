from app.core.database import Base
from app.core.yaml_config import settings
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class PasswordResetToken(Base):
    __tablename__ = f"{settings.table_prefix}password_reset_tokens"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    # Optional direct link to users table for referential integrity
    user_id = Column(
        Integer, ForeignKey(f"{settings.table_prefix}users.id"), nullable=True
    )
    token = Column(String(255), unique=True, index=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="password_reset_tokens")
