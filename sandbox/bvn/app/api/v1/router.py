from typing import Any
from app.schemas.bvn import BVNVerificationRequest, BVNVerificationResponse
from app.services.verification import verify_bvn_with_doja
from fastapi import APIRouter, HTTPException

api_router = APIRouter()


@api_router.post("/verify", response_model=BVNVerificationResponse)
async def verify_bvn(verification_request: BVNVerificationRequest) -> Any:
    """Verify BVN using Doja API."""
    try:
        result = await verify_bvn_with_doja(verification_request.bvn)

        return BVNVerificationResponse(
            bvn_verified=result["success"],
            verification_data=result["data"] if result["success"] else None,
            message=result["message"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/status/{bvn}")
async def get_bvn_status(bvn: str):
    """Get BVN verification status."""
    return {"message": f"BVN {bvn} status check", "bvn": bvn}


@api_router.post("/lookup", response_model=BVNVerificationResponse)
async def lookup_bvn_basic(verification_request: BVNVerificationRequest) -> Any:
    """Basic BVN lookup without full verification."""
    try:
        # For basic lookup, we can use the same verification but with different messaging
        result = await verify_bvn_with_doja(verification_request.bvn)

        return BVNVerificationResponse(
            bvn_verified=result["success"],
            verification_data=result["data"] if result["success"] else None,
            message=f"BVN lookup: {result['message']}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))