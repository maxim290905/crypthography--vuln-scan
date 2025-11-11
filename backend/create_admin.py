#!/usr/bin/env python3
"""
Script to create admin user manually
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User, UserRole
from app.auth import get_password_hash

def create_admin():
    db = SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if admin:
            print("✓ Admin user already exists")
            print(f"  Email: {admin.email}")
            print(f"  Name: {admin.name}")
            print(f"  Role: {admin.role}")
            return
        
        # Create admin user
        password = "admin123"
        admin = User(
            email="admin@example.com",
            name="Admin User",
            password_hash=get_password_hash(password),
            role=UserRole.ADMIN
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        print("✓ Admin user created successfully!")
        print(f"  Email: {admin.email}")
        print(f"  Password: {password}")
        print(f"  Role: {admin.role}")
    except Exception as e:
        print(f"✗ Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()

