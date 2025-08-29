import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Create base class for models (shared across runtime and migrations)
Base = declarative_base()


def _create_engine_for_runtime():
    # Import settings only in normal runtime to avoid requiring secrets during migrations
    try:
        from .yaml_config import settings
    except ImportError:
        from .config import settings

    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=getattr(settings, "debug", False),
    )


def _create_engine_for_migrations():
    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        # During autogenerate (alembic revision) DATABASE_URL may be unset; avoid creating engine.
        return None
    return create_engine(db_url, pool_pre_ping=True, pool_recycle=300)


# Choose engine creation strategy
if os.getenv("MIGRATIONS") == "1":
    engine = _create_engine_for_migrations()
else:
    engine = _create_engine_for_runtime()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import all models to ensure they are registered with Base.metadata
from app.models import oauth_client, oauth_token, user, token_blacklist  # noqa


def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
