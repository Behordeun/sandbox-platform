from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy.sql import func


class SoftDeleteMixin:
    """Mixin that adds soft-delete support to models.

    Models including this mixin gain:
    - is_deleted: Boolean flag
    - deleted_at: Timestamp of deletion
    """

    is_deleted = Column(Boolean, nullable=True, default=False, server_default="false")
    deleted_at = Column(DateTime(timezone=True), nullable=True)

