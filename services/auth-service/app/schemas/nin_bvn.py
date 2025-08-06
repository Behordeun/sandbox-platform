from pydantic import BaseModel, validator
from typing import Optional


class NINBVNVerificationRequest(BaseModel):
    nin: Optional[str] = None
    bvn: Optional[str] = None
    
    @validator('nin')
    def validate_nin(cls, v):
        if v and len(v) != 11:
            raise ValueError('NIN must be 11 digits')
        if v and not v.isdigit():
            raise ValueError('NIN must contain only digits')
        return v
    
    @validator('bvn')
    def validate_bvn(cls, v):
        if v and len(v) != 11:
            raise ValueError('BVN must be 11 digits')
        if v and not v.isdigit():
            raise ValueError('BVN must contain only digits')
        return v
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.nin and not self.bvn:
            raise ValueError('Either NIN or BVN must be provided')


class NINBVNVerificationResponse(BaseModel):
    nin_verified: bool = False
    bvn_verified: bool = False
    verification_data: Optional[dict] = None
    message: str
    
    class Config:
        from_attributes = True


class IdentityVerificationData(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    state_of_origin: Optional[str] = None
    lga_of_origin: Optional[str] = None
    
    class Config:
        from_attributes = True

