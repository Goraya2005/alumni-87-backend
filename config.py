import os

# Environment detection
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

# JWT Configuration
SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretkey")
ALGORITHM = os.environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# CORS Configuration
if ENVIRONMENT == "production":
    FRONTEND_URL = "https://pbg-87.vercel.app"
    CORS_ORIGINS = "https://pbg-87.vercel.app,https://pbg-87.vercel.app/,https://*.vercel.app,http://localhost:3000,http://localhost:3001,http://localhost:3002,http://127.0.0.1:3000,http://127.0.0.1:3001,http://127.0.0.1:3002"
else:
    FRONTEND_URL = "http://localhost:3000"
    CORS_ORIGINS = "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://127.0.0.1:3000,http://127.0.0.1:3001,http://127.0.0.1:3002,https://pbg-87.vercel.app,https://*.vercel.app"

# Now print, after CORS_ORIGINS is defined
print(f"Environment detected: {ENVIRONMENT}")
print(f"CORS Origins: {CORS_ORIGINS}")

# File upload configuration
UPLOAD_DIR = "uploads"
AVATAR_DIR = os.path.join(UPLOAD_DIR, "avatars")
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB 