#!/usr/bin/env python3
"""
Create Admin User Script
Creates initial admin users for the DPI Sandbox Platform
"""

import sys
import os
from pathlib import Path

# Add the auth service to Python path first
auth_service_path = Path(__file__).parent.parent / "services" / "auth-service"
sys.path.insert(0, str(auth_service_path))

# Import after path setup
from app.core.database import SessionLocal  # noqa: E402
from app.crud.user import user_crud  # noqa: E402
from app.schemas.user import UserCreate  # noqa: E402

def create_admin_user(email: str, username: str, password: str, first_name: str, last_name: str):
    """Create an admin user."""
    
    db = SessionLocal()
    
    try:
        # Check if user already exists
        existing_user = user_crud.get_by_email(db, email=email)
        if existing_user:
            print(f"❌ User with email {email} already exists")
            return False
        
        # Create admin user
        user_data = UserCreate(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone_number=None
        )
        
        user = user_crud.create(db, obj_in=user_data)
        
        print("✅ Admin user created successfully:")
        print(f"   Email: {user.email}")
        print(f"   Username: {user.username}")
        print(f"   Name: {user.first_name} {user.last_name}")
        print(f"   ID: {user.id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False
    finally:
        db.close()

def main():
    """Main function to create admin users."""
    
    print("🔧 DPI Sandbox - Admin User Creation")
    print("=" * 50)
    
    # Default admin users
    admin_users = [
        {
            "email": "admin@dpi-sandbox.ng",
            "username": "admin",
            "password": os.getenv("ADMIN_PASSWORD", "AdminPass123!"),
            "first_name": "DPI",
            "last_name": "Administrator"
        },
        {
            "email": "muhammad@dpi-sandbox.ng",
            "username": "muhammad",
            "password": os.getenv("MUHAMMAD_PASSWORD", "MuhammadPass123!"),
            "first_name": "Muhammad",
            "last_name": "Behordeun"
        }
    ]
    
    success_count = 0
    
    for admin_data in admin_users:
        print(f"\n📝 Creating admin user: {admin_data['email']}")
        
        if create_admin_user(**admin_data):
            success_count += 1
    
    print(f"\n🎉 Created {success_count}/{len(admin_users)} admin users successfully!")
    
    if success_count > 0:
        print("\n📋 Admin users can now:")
        print("   • Create user accounts via /api/v1/admin/users")
        print("   • Manage existing users")
        print("   • Reset passwords")
        print("   • Activate/deactivate accounts")
        
        print("\n🔗 API Documentation: http://localhost:8000/docs")
        print("🔗 Admin Endpoints: http://localhost:8000/docs#/admin")

if __name__ == "__main__":
    main()