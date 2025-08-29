from datetime import datetime
from typing import Optional

from app.validators import format_nigerian_phone, validate_nigerian_phone
from pydantic import BaseModel, EmailStr, field_validator


class UserBase(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[str] = "user"  # Add role field


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v

    @field_validator("phone_number")
    def validate_phone(cls, v):
        if v and not validate_nigerian_phone(v):
            raise ValueError(
                "Invalid Nigerian phone number format. Use +234XXXXXXXXXX or 0XXXXXXXXXX"
            )
        return format_nigerian_phone(v) if v else v


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None  # Add role field


class UserLogin(BaseModel):
    identifier: str  # Can be email or username
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    nin_verified: bool
    bvn_verified: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserProfile(BaseModel):
    id: int
    email: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_verified: bool
    nin_verified: bool
    bvn_verified: bool

    class Config:
        from_attributes = True
