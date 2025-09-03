from app.services.proxy import proxy_service
from app.schemas.dpi import SMSSendRequest, SMSBulkRequest, OTPGenerateRequest, OTPVerifyRequest
from fastapi import APIRouter, Request, Body, Depends
from fastapi.security import HTTPBearer
from typing import Any

security = HTTPBearer()
router = APIRouter()

@router.post("/send", tags=["sms"], dependencies=[Depends(security)])
async def send_sms(request: Request, sms_data: SMSSendRequest = Body(...)) -> Any:
    """📱 Send SMS to Nigerian Number"""
    return await proxy_service.proxy_request(request, "sms", "/api/v1/sms/send")

@router.post("/bulk", tags=["sms"], dependencies=[Depends(security)])
async def send_bulk_sms(request: Request, bulk_data: SMSBulkRequest = Body(...)) -> Any:
    """📤 Send Bulk SMS Messages"""
    return await proxy_service.proxy_request(request, "sms", "/api/v1/sms/bulk")

@router.post("/otp/generate", tags=["sms"], dependencies=[Depends(security)])
async def generate_otp(request: Request, otp_data: OTPGenerateRequest = Body(...)) -> Any:
    """🔐 Generate and Send OTP"""
    return await proxy_service.proxy_request(request, "sms", "/api/v1/sms/otp/generate")

@router.post("/otp/verify", tags=["sms"], dependencies=[Depends(security)])
async def verify_otp(request: Request, otp_data: OTPVerifyRequest = Body(...)) -> Any:
    """✅ Verify OTP Code"""
    return await proxy_service.proxy_request(request, "sms", "/api/v1/sms/otp/verify")

@router.get("/status/{message_id}", tags=["sms"], dependencies=[Depends(security)])
async def get_message_status(request: Request, message_id: str) -> Any:
    """📊 Check Message Delivery Status"""
    return await proxy_service.proxy_request(request, "sms", f"/api/v1/sms/status/{message_id}")

@router.get("/balance", tags=["sms"], dependencies=[Depends(security)])
async def get_sms_balance(request: Request) -> Any:
    """💰 Check SMS Credit Balance"""
    return await proxy_service.proxy_request(request, "sms", "/api/v1/sms/balance")

@router.get("/templates", tags=["sms"], dependencies=[Depends(security)])
async def get_message_templates(request: Request) -> Any:
    """📝 Get Message Templates"""
    return await proxy_service.proxy_request(request, "sms", "/api/v1/sms/templates")
