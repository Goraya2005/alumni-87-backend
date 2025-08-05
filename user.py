from models import User, Member
from schemas import UserCreate, User as UserSchema, MemberCreate
from database import SessionLocal
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
import os
import uuid
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(tags=["users"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/token")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

class UserRegistrationRequest(BaseModel):
    username: str
    email: str
    password: str
    name: Optional[str] = None
    role: Optional[str] = "USER"
    # Member profile fields
    registration_number: str
    department: str
    address: str
    city: str
    country: str
    phone: Optional[str] = None
    bio: Optional[str] = None

@router.post("/register", response_model=UserSchema)
def register(user_data: UserRegistrationRequest, db: Session = Depends(get_db)):
    # Check if username already exists
    db_user = get_user_by_username(db, user_data.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if email already exists
    db_user = get_user_by_email(db, user_data.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        id=user_id,
        username=user_data.username,
        email=user_data.email,
        name=user_data.name,
        role=user_data.role,
        password=hashed_password
    )
    db.add(db_user)
    
    # Create member profile
    member_id = str(uuid.uuid4())
    db_member = Member(
        id=member_id,
        user_id=user_id,
        registration_number=user_data.registration_number,
        department=user_data.department,
        address=user_data.address,
        city=user_data.city,
        country=user_data.country,
        phone=user_data.phone,
        bio=user_data.bio,
        is_profile_complete=True  # Since we're creating it with all required fields
    )
    db.add(db_member)
    
    db.commit()
    db.refresh(db_user)
    db.refresh(db_member)
    
    return db_user

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserSchema

@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserSchema)
def read_users_me(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = decode_access_token(token)
    user = get_user_by_username(db, username)
    if user:
        return user
    raise HTTPException(status_code=401, detail="Invalid token")

@router.get("/profile", response_model=dict)
def get_user_profile(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = decode_access_token(token)
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get member profile
    member = db.query(Member).filter(Member.user_id == user.id).first()
    
    # Prepare member data if it exists
    member_data = None
    if member:
        member_data = {
            "id": member.id,
            "registrationNumber": member.registration_number,
            "department": member.department,
            "address": member.address,
            "city": member.city,
            "country": member.country,
            "phone": member.phone,
            "bio": member.bio,
            "avatarUrl": member.avatar_url,
            "isProfileComplete": member.is_profile_complete,
            "createdAt": member.created_at,
            "updatedAt": member.updated_at
        }
    
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "name": user.name,
            "role": user.role,
            "created_at": user.created_at
        },
        "member": member_data
    }

@router.delete("/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Delete member profile if exists
    member = db.query(Member).filter(Member.user_id == user_id).first()
    if member:
        db.delete(member)
    db.delete(user)
    db.commit()
    return {"ok": True}

class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None

@router.put("/{user_id}", response_model=UserSchema)
def update_user(user_id: str, update: UserUpdateRequest = Body(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if update.username:
        # Check for username conflict
        if db.query(User).filter(User.username == update.username, User.id != user_id).first():
            raise HTTPException(status_code=400, detail="Username already taken")
        user.username = update.username
    if update.password:
        user.password = get_password_hash(update.password)
    if update.name:
        user.name = update.name
    if update.email:
        # Check for email conflict
        if db.query(User).filter(User.email == update.email, User.id != user_id).first():
            raise HTTPException(status_code=400, detail="Email already taken")
        user.email = update.email
    if update.role:
        user.role = update.role
    db.commit()
    db.refresh(user)
    return user

@router.get("/admin/all", response_model=list)
def read_all_users_admin(
    skip: int = 0, 
    limit: int = 100, 
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """Get all users with their member information (admin only)"""
    # Verify authentication and admin role
    username = decode_access_token(token)
    current_user = get_user_by_username(db, username)
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid authentication")
    
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get all users with their member profiles
    users = db.query(User).offset(skip).limit(limit).all()
    
    result = []
    for user in users:
        from models import Member
        member = db.query(Member).filter(Member.user_id == user.id).first()
        
        user_data = {
            "id": user.id,
            "name": user.name,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "createdAt": user.created_at,
            "updatedAt": user.updated_at,
            "member": None
        }
        
        if member:
            user_data["member"] = {
                "id": member.id,
                "registrationNumber": member.registration_number,
                "department": member.department,
                "address": member.address,
                "city": member.city,
                "country": member.country,
                "phone": member.phone,
                "avatarUrl": member.avatar_url,
                "bio": member.bio,
                "isProfileComplete": member.is_profile_complete,
                "createdAt": member.created_at,
                "updatedAt": member.updated_at
            }
        
        result.append(user_data)
    
    return result

@router.put("/profile")
def update_own_user_profile(
    update: UserUpdateRequest = Body(...),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    username = decode_access_token(token)
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if update.username:
        if db.query(User).filter(User.username == update.username, User.id != user.id).first():
            raise HTTPException(status_code=400, detail="Username already taken")
        user.username = update.username
    if update.password:
        user.password = get_password_hash(update.password)
    if update.name:
        user.name = update.name
    if update.email:
        if db.query(User).filter(User.email == update.email, User.id != user.id).first():
            raise HTTPException(status_code=400, detail="Email already taken")
        user.email = update.email
    db.commit()
    db.refresh(user)
    return user
