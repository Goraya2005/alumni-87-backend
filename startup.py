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
    print("Startup complete!")

if __name__ == "__main__":
    startup() 