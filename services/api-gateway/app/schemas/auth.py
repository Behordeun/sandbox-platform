from pydantic import BaseModel, EmailStr
from typing import Optional

class UserLogin(BaseModel):
    identifier: str
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None

class PasswordReset(BaseModel):
    new_password: str

class OAuth2TokenRequest(BaseModel):
    grant_type: str
    client_id: str
    client_secret: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None

class OAuth2ClientCreate(BaseModel):
    name: str
    description: Optional[str] = None
    redirect_uris: list[str] = []