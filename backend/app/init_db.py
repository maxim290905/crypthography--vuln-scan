"""
Database initialization script
Run this to create initial admin user
"""
from app.database import SessionLocal
from app.models import User, UserRole
from app.auth import get_password_hash

def init_db():
    db = SessionLocal()
    
    # Check if admin exists
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    if admin:
        print("Admin user already exists")
        return
    
    # Create admin user
    admin = User(
        email="admin@example.com",
        name="Admin User",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN
    )
    db.add(admin)
    db.commit()
    print("Admin user created: admin@example.com / admin123")

if __name__ == "__main__":
    init_db()

