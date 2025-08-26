from typing import Optional

from pydantic import BaseModel, field_validator


class BVNVerificationRequest(BaseModel):
    bvn: str

    @field_validator("bvn")
    def validate_bvn(cls, v):
        if len(v) != 11:
            raise ValueError("BVN must be 11 digits")
        if not v.isdigit():
            raise ValueError("BVN must contain only digits")
        return v


class BVNVerificationResponse(BaseModel):
    bvn_verified: bool = False
    verification_data: Optional[dict] = None
    message: str

    class Config:
        from_attributes = True


class BVNIdentityData(BaseModel):
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
    bvn: Optional[str] = None
    enrollment_bank: Optional[str] = None
    enrollment_branch: Optional[str] = None
    watch_listed: Optional[str] = None

    class Config:
        from_attributes = True
