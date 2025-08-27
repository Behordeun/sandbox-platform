#!/usr/bin/env python3
"""
Centralized Database Migration Script
Runs migrations for all services using the consolidated PostgreSQL database
"""

import os
import sys
import subprocess
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
    
    # Get database configuration
    config = get_config(environment)
    db_config = config.get("database", {})
    db_url = db_config.get("url")
    
    if not db_url:
        print("❌ Database URL not found in configuration")
        return False
    
    print(f"📊 Database: {db_url.split('@')[1] if '@' in db_url else db_url}")
    
    # Services with migrations
    services_with_migrations = [
        {
            "name": "auth-service",
            "path": "services/auth-service",
            "has_alembic": True
        }
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
                result = subprocess.run(
                    ["alembic", "upgrade", "head"],
                    env=env,
                    capture_output=True,
                    text=True
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

def create_database():
    """Create the database if it doesn't exist."""
    
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