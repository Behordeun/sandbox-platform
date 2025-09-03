from app.services.proxy import proxy_service
from app.schemas.dpi import BVNVerifyRequest, BVNLookupRequest, BVNMatchRequest
from fastapi import APIRouter, Request, Body, Depends
from fastapi.security import HTTPBearer
from typing import Any

security = HTTPBearer()
router = APIRouter()

@router.post("/verify", tags=["bvn"], dependencies=[Depends(security)])
async def verify_bvn(request: Request, bvn_data: BVNVerifyRequest = Body(...)) -> Any:
    """🇳🇬 Verify Bank Verification Number (BVN)"""
    return await proxy_service.proxy_request(request, "bvn", "/api/v1/bvn/verify")

@router.get("/status/{bvn}", tags=["bvn"], dependencies=[Depends(security)])
async def get_bvn_status(request: Request, bvn: str) -> Any:
    """📊 Get BVN Verification Status"""
    return await proxy_service.proxy_request(request, "bvn", f"/api/v1/bvn/status/{bvn}")

@router.post("/lookup", tags=["bvn"], dependencies=[Depends(security)])
async def lookup_bvn(request: Request, bvn_data: BVNLookupRequest = Body(...)) -> Any:
    """🔍 Basic BVN Lookup"""
    return await proxy_service.proxy_request(request, "bvn", "/api/v1/bvn/lookup")

@router.post("/match", tags=["bvn"], dependencies=[Depends(security)])
async def match_bvn(request: Request, match_data: BVNMatchRequest = Body(...)) -> Any:
    """🔗 Match BVN with User Data"""
    return await proxy_service.proxy_request(request, "bvn", "/api/v1/bvn/match")

@router.get("/banks", tags=["bvn"], dependencies=[Depends(security)])
async def get_supported_banks(request: Request) -> Any:
    """🏦 Get Supported Nigerian Banks"""
    return await proxy_service.proxy_request(request, "bvn", "/api/v1/bvn/banks")
