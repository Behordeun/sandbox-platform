from typing import Optional
from pydantic import BaseModel, field_validator


class NINVerificationRequest(BaseModel):
    nin: str

    @field_validator("nin")
    def validate_nin(cls, v):
        if len(v) != 11:
            raise ValueError("NIN must be 11 digits")
        if not v.isdigit():
            raise ValueError("NIN must contain only digits")
        return v


class NINVerificationResponse(BaseModel):
    nin_verified: bool = False
    verification_data: Optional[dict] = None
    message: str

    class Config:
        from_attributes = True


class IdentityData(BaseModel):
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
    nin: Optional[str] = None
    photo: Optional[str] = None

    class Config:
        from_attributes = True