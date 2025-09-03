from app.services.proxy import proxy_service
from app.schemas.dpi import NINVerifyRequest, NINLookupRequest
from fastapi import APIRouter, Request, Body, Depends
from fastapi.security import HTTPBearer
from typing import Any

security = HTTPBearer()
router = APIRouter()

@router.post("/verify", tags=["nin"], dependencies=[Depends(security)])
async def verify_nin(request: Request, nin_data: NINVerifyRequest = Body(...)) -> Any:
    """🇳🇬 Verify Nigerian Identity Number (NIN)"""
    return await proxy_service.proxy_request(request, "nin", "/api/v1/nin/verify")

@router.get("/status/{nin}", tags=["nin"], dependencies=[Depends(security)])
async def get_nin_status(request: Request, nin: str) -> Any:
    """📊 Get NIN Verification Status"""
    return await proxy_service.proxy_request(request, "nin", f"/api/v1/nin/status/{nin}")

@router.post("/lookup", tags=["nin"], dependencies=[Depends(security)])
async def lookup_nin(request: Request, nin_data: NINLookupRequest = Body(...)) -> Any:
    """🔍 Basic NIN Lookup"""
    return await proxy_service.proxy_request(request, "nin", "/api/v1/nin/lookup")
