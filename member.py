from models import Member, User
from schemas import MemberCreate, Member as MemberSchema
from database import SessionLocal
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uuid
from fastapi.security import OAuth2PasswordBearer
from user import decode_access_token

router = APIRouter(tags=["members"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/token")

@router.post("/", response_model=MemberSchema)
def create_member(member: MemberCreate, db: Session = Depends(get_db)):
    member_id = str(uuid.uuid4())
    db_member = Member(id=member_id, **member.dict())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return db_member

@router.get("/", response_model=List[dict])
def read_members(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all members with their user information"""
    members = db.query(Member).offset(skip).limit(limit).all()
    
    result = []
    for member in members:
        user = db.query(User).filter(User.id == member.user_id).first()
        if user:
            result.append({
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
                "updatedAt": member.updated_at,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "createdAt": user.created_at
                }
            })
    
    return result

@router.get("/{member_id}", response_model=dict)
def read_member(member_id: str, db: Session = Depends(get_db)):
    """Get a specific member with user information"""
    member = db.query(Member).filter(Member.id == member_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    user = db.query(User).filter(User.id == member.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
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
        "updatedAt": member.updated_at,
        "user": {
            "id": user.id,
            "name": user.name,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "createdAt": user.created_at
        }
    }

@router.get("/user/{user_id}", response_model=dict)
def read_member_by_user_id(user_id: str, db: Session = Depends(get_db)):
    """Get member profile by user ID"""
    member = db.query(Member).filter(Member.user_id == user_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member profile not found")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
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
        "updatedAt": member.updated_at,
        "user": {
            "id": user.id,
            "name": user.name,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "createdAt": user.created_at
        }
    }

@router.put("/{member_id}", response_model=dict)
def update_member(member_id: str, member_data: Dict[str, Any] = Body(...), db: Session = Depends(get_db)):
    """Update member profile by member ID"""
    try:
        print(f"Updating member {member_id} with data: {member_data}")
        
        db_member = db.query(Member).filter(Member.id == member_id).first()
        if not db_member:
            raise HTTPException(status_code=404, detail="Member not found")
        
        # Update member fields
        update_fields = [
            'registration_number', 'department', 'address', 'city', 'country',
            'phone', 'avatar_url', 'bio'
        ]
        
        for field in update_fields:
            if field in member_data and member_data[field] is not None:
                setattr(db_member, field, member_data[field])
        
        db_member.is_profile_complete = True
        db.commit()
        db.refresh(db_member)
        
        # Return updated member with user data
        user = db.query(User).filter(User.id == db_member.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        result = {
            "id": db_member.id,
            "registrationNumber": db_member.registration_number,
            "department": db_member.department,
            "address": db_member.address,
            "city": db_member.city,
            "country": db_member.country,
            "phone": db_member.phone,
            "avatarUrl": db_member.avatar_url,
            "bio": db_member.bio,
            "isProfileComplete": db_member.is_profile_complete,
            "createdAt": db_member.created_at,
            "updatedAt": db_member.updated_at,
            "user": {
                "id": user.id,
                "name": user.name,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "createdAt": user.created_at
            }
        }
        
        print(f"Member {member_id} updated successfully")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating member {member_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/user/{user_id}", response_model=dict)
def update_member_by_user_id(user_id: str, member_data: dict, db: Session = Depends(get_db)):
    """Update member profile by user ID"""
    member = db.query(Member).filter(Member.user_id == user_id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member profile not found")
    
    # Update member fields
    update_fields = [
        'registration_number', 'department', 'address', 'city', 'country',
        'phone', 'avatar_url', 'bio'
    ]
    
    for field in update_fields:
        if field in member_data:
            setattr(member, field, member_data[field])
    
    member.is_profile_complete = True
    db.commit()
    db.refresh(member)
    
    # Return updated member with user data
    user = db.query(User).filter(User.id == user_id).first()
    return {
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
        "updatedAt": member.updated_at,
        "user": {
            "id": user.id,
            "name": user.name,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "createdAt": user.created_at
        }
    }

@router.delete("/{member_id}")
def delete_member(member_id: str, db: Session = Depends(get_db)):
    db_member = db.query(Member).filter(Member.id == member_id).first()
    if not db_member:
        raise HTTPException(status_code=404, detail="Member not found")
    db.delete(db_member)
    db.commit()
    return {"ok": True}

@router.put("/profile")
def update_own_member_profile(
    member_data: dict = Body(...),
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    username = decode_access_token(token)
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    member = db.query(Member).filter(Member.user_id == user.id).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member profile not found")
    update_fields = [
        'registration_number', 'department', 'address', 'city', 'country',
        'phone', 'avatar_url', 'bio'
    ]
    for field in update_fields:
        if field in member_data and member_data[field] is not None:
            setattr(member, field, member_data[field])
    member.is_profile_complete = True
    db.commit()
    db.refresh(member)
    return {
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
        "updatedAt": member.updated_at,
        "user": {
            "id": user.id,
            "name": user.name,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "createdAt": user.created_at
        }
    } 