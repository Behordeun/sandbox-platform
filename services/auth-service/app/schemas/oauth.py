from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime


class OAuthClientBase(BaseModel):
    client_name: str
    client_description: Optional[str] = None
    client_uri: Optional[str] = None
    redirect_uris: List[str]
    scope: str = "openid profile email"


class OAuthClientCreate(OAuthClientBase):
    grant_types: List[str] = ["authorization_code", "refresh_token"]
    response_types: List[str] = ["code"]
    is_confidential: bool = True


class OAuthClientResponse(OAuthClientBase):
    id: int
    client_id: str
    client_secret: str
    grant_types: List[str]
    response_types: List[str]
    is_active: bool
    is_confidential: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuthorizeRequest(BaseModel):
    response_type: str
    client_id: str
    redirect_uri: str
    scope: Optional[str] = None
    state: Optional[str] = None
    
    @validator('response_type')
    def validate_response_type(cls, v):
        if v not in ['code', 'token']:
            raise ValueError('Invalid response_type')
        return v


class AuthorizeResponse(BaseModel):
    authorization_code: str
    state: Optional[str] = None
    expires_in: int


class TokenRequest(BaseModel):
    grant_type: str
    client_id: str
    client_secret: Optional[str] = None
    code: Optional[str] = None
    redirect_uri: Optional[str] = None
    refresh_token: Optional[str] = None
    
    @validator('grant_type')
    def validate_grant_type(cls, v):
        valid_types = ['authorization_code', 'refresh_token', 'client_credentials']
        if v not in valid_types:
            raise ValueError('Invalid grant_type')
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: int
    refresh_token: Optional[str] = None
    scope: Optional[str] = None


class TokenIntrospectionRequest(BaseModel):
    token: str
    token_type_hint: Optional[str] = None


class TokenIntrospectionResponse(BaseModel):
    active: bool
    client_id: Optional[str] = None
    username: Optional[str] = None
    scope: Optional[str] = None
    exp: Optional[int] = None
    iat: Optional[int] = None
    sub: Optional[str] = None

