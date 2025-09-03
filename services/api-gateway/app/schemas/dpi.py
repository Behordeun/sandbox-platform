from pydantic import BaseModel
from typing import Optional, List

# NIN Schemas
class NINVerifyRequest(BaseModel):
    nin: str

class NINLookupRequest(BaseModel):
    nin: str

# BVN Schemas  
class BVNVerifyRequest(BaseModel):
    bvn: str

class BVNLookupRequest(BaseModel):
    bvn: str

class BVNMatchRequest(BaseModel):
    bvn: str
    first_name: str
    last_name: str
    date_of_birth: Optional[str] = None

# SMS Schemas
class SMSSendRequest(BaseModel):
    to: str
    message: str
    sender_id: Optional[str] = None

class SMSBulkRequest(BaseModel):
    recipients: List[str]
    message: str
    sender_id: Optional[str] = None

class OTPGenerateRequest(BaseModel):
    phone_number: str
    length: Optional[int] = 6
    expiry_minutes: Optional[int] = 5

class OTPVerifyRequest(BaseModel):
    phone_number: str
    otp_code: str

# AI Schemas
class AIChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    context: Optional[str] = None

class AIGenerateRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 150
    temperature: Optional[float] = 0.7

class AIAnalyzeRequest(BaseModel):
    text: str
    analysis_type: Optional[str] = "sentiment"

class AITranslateRequest(BaseModel):
    text: str
    source_language: Optional[str] = "auto"
    target_language: str