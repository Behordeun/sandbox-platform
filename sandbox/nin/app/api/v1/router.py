from typing import Any
from app.schemas.nin import NINVerificationRequest, NINVerificationResponse
from app.services.verification import verify_nin_with_doja
from fastapi import APIRouter, HTTPException

api_router = APIRouter()


@api_router.post("/verify", response_model=NINVerificationResponse)
async def verify_nin(verification_request: NINVerificationRequest) -> Any:
    """Verify NIN using Doja API."""
    try:
        result = await verify_nin_with_doja(verification_request.nin)
        
        return NINVerificationResponse(
            nin_verified=result["success"],
            verification_data=result["data"] if result["success"] else None,
            message=result["message"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/status/{nin}")
async def get_nin_status(nin: str):
    """Get NIN verification status."""
    return {"message": f"NIN {nin} status check", "nin": nin}


@api_router.post("/lookup", response_model=NINVerificationResponse)
async def lookup_nin_basic(verification_request: NINVerificationRequest) -> Any:
    """Basic NIN lookup without full verification."""
    try:
        # For basic lookup, we can use the same verification but with different messaging
        result = await verify_nin_with_doja(verification_request.nin)
        
        return NINVerificationResponse(
            nin_verified=result["success"],
            verification_data=result["data"] if result["success"] else None,
            message=f"NIN lookup: {result['message']}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))