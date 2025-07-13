from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import shutil
from datetime import datetime
import uuid
from user import router as user_router, oauth2_scheme
from member import router as member_router

app = FastAPI(title="PBG87 Backend API", version="1.0.0")

# Allow CORS for frontend (adjust origin as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://127.0.0.1:3000", "http://127.0.0.1:3001", "http://127.0.0.1:3002"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*", "Content-Type", "Authorization", "X-Requested-With"],
    expose_headers=["*"],
)

# Create uploads directory if it doesn't exist
UPLOAD_DIR = "uploads"
AVATAR_DIR = os.path.join(UPLOAD_DIR, "avatars")
os.makedirs(AVATAR_DIR, exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.get("/")
def read_root():
    return {"message": "PBG87 Backend API is running!", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "Backend is operational"}

# Include API routes
app.include_router(user_router, prefix="/api/users", tags=["users"])
app.include_router(member_router, prefix="/api/members", tags=["members"])



@app.post("/api/upload/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    token: str = Depends(oauth2_scheme)
):
    """Upload avatar for the authenticated user"""
    from user import decode_access_token, get_user_by_username
    from member import get_db
    from models import Member
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Validate file size (max 5MB)
    if file.size and file.size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size must be less than 5MB")
    
    # Get user from token
    username = decode_access_token(token)
    db = next(get_db())
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get member profile
    member = db.query(Member).filter(Member.user_id == user.id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member profile not found")
    
    # Generate unique filename
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_extension}"
    file_path = os.path.join(AVATAR_DIR, unique_filename)
    
    try:
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Update member's avatar_url
        member.avatar_url = f"/uploads/avatars/{unique_filename}"
        db.commit()
        
        return {
            "message": "Avatar uploaded successfully",
            "avatar_url": member.avatar_url
        }
        
    except Exception as e:
        # Clean up file if database update fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}") 