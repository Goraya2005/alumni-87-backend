import os
from database import engine
from models import Base

def init_database():
    """Initialize the database by creating all tables"""
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")

def create_upload_directories():
    """Create necessary upload directories"""
    from config import UPLOAD_DIR, AVATAR_DIR
    
    try:
        os.makedirs(AVATAR_DIR, exist_ok=True)
        print(f"Upload directories created: {AVATAR_DIR}")
    except Exception as e:
        print(f"Error creating upload directories: {e}")

def startup():
    """Run all startup tasks"""
    print("Starting PBG87 Backend...")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")
    print(f"Database URL: {os.getenv('DATABASE_URL', 'sqlite:///./app.db')}")
    
    init_database()
    create_upload_directories()
    
    # Check database connection and log member count
    try:
        from database import SessionLocal
        from models import User, Member
        db = SessionLocal()
        user_count = db.query(User).count()
        member_count = db.query(Member).count()
        admin_count = db.query(User).filter(User.role == 'ADMIN').count()
        print(f"Database initialized with {user_count} users, {member_count} members, {admin_count} admins")
        db.close()
    except Exception as e:
        print(f"Warning: Could not query database: {e}")
    
    print("Startup complete!")

if __name__ == "__main__":
    startup() 