#!/usr/bin/env python3
"""
Centralized Database Migration Script
Runs migrations for all services using the consolidated PostgreSQL database
"""

import os
import subprocess
import sys
from pathlib import Path

# Add config to path
sys.path.append(str(Path(__file__).parent.parent / "config"))
try:
    from config_loader import get_config
except ImportError:
    print("❌ Config loader not found. Please ensure config directory exists.")
    sys.exit(1)


def run_migrations():
    """Run database migrations for all services."""

    # Set environment
    environment = os.getenv("ENVIRONMENT", "development")
    print(f"Running migrations for environment: {environment}")

    # Get database URL from environment variable first, then config
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        # Fallback to config
        config = get_config(environment)
        db_config = config.get("database", {})
        db_url = db_config.get("url")

    if not db_url:
        print("❌ Database URL not found in environment or configuration")
        return False

    print(f"📊 Database: {db_url.split('@')[1] if '@' in db_url else db_url}")

    # Services with migrations
    services_with_migrations = [
        {"name": "auth-service", "path": "services/auth-service", "has_alembic": True}
    ]

    success = True

    for service in services_with_migrations:
        print(f"\n🔄 Running migrations for {service['name']}...")

        service_path = Path(__file__).parent.parent / service["path"]
        if not service_path.exists():
            print(f"⚠️  Service path not found: {service_path}")
            continue

        if service["has_alembic"]:
            # Run Alembic migrations
            try:
                # Change to service directory
                original_cwd = os.getcwd()
                os.chdir(service_path)

                # Set database URL environment variable
                env = os.environ.copy()
                env["DATABASE_URL"] = db_url

                # Run alembic upgrade
                # Try different alembic paths
                alembic_cmd = None
                for cmd in ["python3", "python"]:
                    try:
                        subprocess.run(
                            [cmd, "-m", "alembic", "--version"],
                            capture_output=True,
                            check=True,
                        )
                        alembic_cmd = [cmd, "-m", "alembic"]
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue

                if not alembic_cmd:
                    print(f"⚠️  Alembic not found for {service['name']}. Falling back to direct table creation.")
                    # Fallback: create tables via SQLAlchemy metadata
                    if create_tables_directly(service["path"], db_url):
                        print(f"✅ {service['name']} tables ensured via SQLAlchemy")
                        os.chdir(original_cwd)
                        continue
                    else:
                        success = False
                        os.chdir(original_cwd)
                        continue

                # Ensure migration context flags
                env["MIGRATIONS"] = "1"
                result = subprocess.run(
                    alembic_cmd + ["upgrade", "head"],
                    env=env,
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    print(f"✅ {service['name']} migrations completed successfully")
                else:
                    print(f"❌ {service['name']} migrations failed:")
                    print(result.stderr)
                    success = False

                # Return to original directory
                os.chdir(original_cwd)

            except Exception as e:
                print(f"❌ Error running migrations for {service['name']}: {e}")
                success = False
                os.chdir(original_cwd)
        else:
            # For services without Alembic, create tables directly
            print(f"📝 Creating tables for {service['name']} (no Alembic)")
            # This would be implemented per service as needed

    return success


def create_tables_directly(service_rel_path: str, db_url: str) -> bool:
    """Create service tables directly using SQLAlchemy metadata.

    This is a fallback when Alembic is not available in the runtime environment.
    """
    try:
        from importlib import import_module
        from sqlalchemy import create_engine

        # Make sure service package is importable
        service_path = Path(__file__).parent.parent / service_rel_path
        sys.path.insert(0, str(service_path))

        # Ensure DB URL visible to service settings/engine modules
        os.environ.setdefault("DATABASE_URL", db_url)
        os.environ.setdefault("MIGRATIONS", "1")

        # Import database and models to register metadata
        db_mod = import_module("app.core.database")
        # Import models to ensure they are attached to Base.metadata
        import_module("app.models.user")
        import_module("app.models.oauth_client")
        import_module("app.models.oauth_token")
        import_module("app.models.password_reset")
        import_module("app.models.token_blacklist")

        Base = getattr(db_mod, "Base")
        engine = create_engine(db_url, pool_pre_ping=True)
        Base.metadata.create_all(bind=engine)
        return True
    except Exception as e:
        print(f"❌ Direct table creation failed: {e}")
        return False


def create_database():
    """Create the database if it doesn't exist."""

    # Get database URL from environment variable first, then config
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        # Fallback to config
        environment = os.getenv("ENVIRONMENT", "development")
        config = get_config(environment)
        db_config = config.get("database", {})
        db_url = db_config.get("url")

    if not db_url or not db_url.startswith("postgresql://"):
        print("⚠️  Not a PostgreSQL database, skipping database creation")
        return True

    # Extract database name and connection info
    try:
        from urllib.parse import urlparse

        parsed = urlparse(db_url)
        db_name = parsed.path[1:]  # Remove leading slash

        # Create connection URL without database name
        admin_url = f"postgresql://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}/postgres"

        print(f"🔧 Creating database '{db_name}' if it doesn't exist...")

        # Try to create database
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

        conn = psycopg2.connect(admin_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        if cursor.fetchone():
            print(f"✅ Database '{db_name}' already exists")
        else:
            cursor.execute(f'CREATE DATABASE "{db_name}"')
            print(f"✅ Database '{db_name}' created successfully")

        cursor.close()
        conn.close()
        return True

    except ImportError:
        print("⚠️  psycopg2 not installed. Install with: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False


def main():
    """Main migration function."""

    print("🗄️  Sandbox Platform - Database Migration")
    print("=" * 50)

    # Create database if needed
    if not create_database():
        print("❌ Failed to create database")
        sys.exit(1)

    # Run migrations
    if run_migrations():
        print("\n✅ All migrations completed successfully!")
        print("\n📋 Next steps:")
        print("   1. Start your services")
        print("   2. Check database tables with prefixes (auth_, config_, etc.)")
        print("   3. Verify application connectivity")
    else:
        print("\n❌ Some migrations failed. Check the errors above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
