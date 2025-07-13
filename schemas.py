from pydantic import BaseModel, EmailStr
from typing import Optional

class MemberBase(BaseModel):
    registration_number: str
    department: str
    address: str
    city: str
    country: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    is_profile_complete: Optional[bool] = False

class MemberCreate(MemberBase):
    pass

class Member(MemberBase):
    id: str
    user_id: str
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    name: Optional[str] = None
    username: str
    email: EmailStr
    role: Optional[str] = "USER"

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    member: Optional[Member] = None
    class Config:
        from_attributes = True 