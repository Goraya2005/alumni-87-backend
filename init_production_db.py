#!/usr/bin/env python3
"""
Database initialization script for production deployment
This script ensures the database is properly set up with all required tables
"""

import os
import sys
from database import engine, SessionLocal
from models import Base, User, Member
from user import get_password_hash
import uuid

def init_database():
    """Initialize database tables"""
    try:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"✗ Error creating database tables: {e}")
        return False

def check_database_connection():
    """Check if database connection is working"""
    try:
        db = SessionLocal()
        user_count = db.query(User).count()
        member_count = db.query(Member).count()
        print(f"✓ Database connection successful!")
        print(f"  - Users: {user_count}")
        print(f"  - Members: {member_count}")
        db.close()
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def create_default_admin():
    """Create a default admin user if none exists"""
    try:
        db = SessionLocal()
        
        # Check if any admin users exist
        admin_count = db.query(User).filter(User.role == 'ADMIN').count()
        if admin_count > 0:
            print(f"✓ Admin users already exist ({admin_count} found)")
            db.close()
            return True
        
        # Create default admin user
        admin_id = str(uuid.uuid4())
        admin_user = User(
            id=admin_id,
            username="admin",
            email="admin@pbg87.com",
            name="System Administrator",
            role="ADMIN",
            password=get_password_hash("admin123")  # Change this in production!
        )
        db.add(admin_user)
        
        # Create corresponding member profile
        member_id = str(uuid.uuid4())
        admin_member = Member(
            id=member_id,
            user_id=admin_id,
            registration_number="ADMIN001",
            department="Administration",
            address="System",
            city="System",
            country="System",
            is_profile_complete=True
        )
        db.add(admin_member)
        
        db.commit()
        print("✓ Default admin user created successfully!")
        print("  - Username: admin")
        print("  - Password: admin123 (CHANGE THIS!)")
        db.close()
        return True
        
    except Exception as e:
        print(f"✗ Error creating default admin: {e}")
        return False

def main():
    """Main initialization function"""
    print("PBG87 Database Initialization")
    print("=" * 40)
    
    # Check environment
    env = os.getenv('ENVIRONMENT', 'development')
    db_url = os.getenv('DATABASE_URL', 'sqlite:///./app.db')
    print(f"Environment: {env}")
    print(f"Database URL: {db_url}")
    print("-" * 40)
    
    success = True
    
    # Initialize database
    if not init_database():
        success = False
    
    # Check connection
    if not check_database_connection():
        success = False
    
    # Create default admin only in development or if requested
    if env == 'development' or '--create-admin' in sys.argv:
        if not create_default_admin():
            success = False
    
    print("-" * 40)
    if success:
        print("✓ Database initialization completed successfully!")
    else:
        print("✗ Database initialization failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
