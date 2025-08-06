from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any
import httpx
import asyncio

from app.dependencies.database import get_db
from app.dependencies.auth import get_current_active_user
from app.crud.user import user_crud
from app.schemas.nin_bvn import NINBVNVerificationRequest, NINBVNVerificationResponse
from app.models.user import User
from app.core.config import settings

router = APIRouter()


async def verify_nin_with_doja(nin: str) -> dict:
    """Verify NIN using Doja API."""
    if not settings.doja_api_key:
        raise HTTPException(
            status_code=500,
            detail="NIN verification service not configured"
        )
    
    headers = {
        "Authorization": f"Bearer {settings.doja_api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "nin": nin
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.doja_base_url}/api/v1/kyc/nin",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "data": data.get("entity", {}),
                    "message": "NIN verified successfully"
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"NIN verification failed: {response.text}"
                }
        except httpx.TimeoutException:
            return {
                "success": False,
                "data": None,
                "message": "NIN verification service timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"NIN verification error: {str(e)}"
            }


async def verify_bvn_with_doja(bvn: str) -> dict:
    """Verify BVN using Doja API."""
    if not settings.doja_api_key:
        raise HTTPException(
            status_code=500,
            detail="BVN verification service not configured"
        )
    
    headers = {
        "Authorization": f"Bearer {settings.doja_api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "bvn": bvn
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.doja_base_url}/api/v1/kyc/bvn",
                json=payload,
                headers=headers,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "data": data.get("entity", {}),
                    "message": "BVN verified successfully"
                }
            else:
                return {
                    "success": False,
                    "data": None,
                    "message": f"BVN verification failed: {response.text}"
                }
        except httpx.TimeoutException:
            return {
                "success": False,
                "data": None,
                "message": "BVN verification service timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"BVN verification error: {str(e)}"
            }


@router.post("/verify-nin-bvn", response_model=NINBVNVerificationResponse)
async def verify_nin_bvn(
    *,
    db: Session = Depends(get_db),
    verification_request: NINBVNVerificationRequest,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Verify NIN and/or BVN for the current user."""
    nin_verified = False
    bvn_verified = False
    verification_data = {}
    messages = []
    
    # Verify NIN if provided
    if verification_request.nin:
        nin_result = await verify_nin_with_doja(verification_request.nin)
        if nin_result["success"]:
            nin_verified = True
            verification_data["nin_data"] = nin_result["data"]
            messages.append("NIN verified successfully")
            
            # Update user record
            user_crud.verify_nin(
                db, 
                user=current_user, 
                nin=verification_request.nin,
                verification_data=nin_result["data"]
            )
        else:
            messages.append(nin_result["message"])
    
    # Verify BVN if provided
    if verification_request.bvn:
        bvn_result = await verify_bvn_with_doja(verification_request.bvn)
        if bvn_result["success"]:
            bvn_verified = True
            verification_data["bvn_data"] = bvn_result["data"]
            messages.append("BVN verified successfully")
            
            # Update user record
            user_crud.verify_bvn(
                db, 
                user=current_user, 
                bvn=verification_request.bvn,
                verification_data=bvn_result["data"]
            )
        else:
            messages.append(bvn_result["message"])
    
    return NINBVNVerificationResponse(
        nin_verified=nin_verified,
        bvn_verified=bvn_verified,
        verification_data=verification_data if verification_data else None,
        message="; ".join(messages) if messages else "No verification performed"
    )


@router.get("/verification-status", response_model=dict)
def get_verification_status(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get current user's verification status."""
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "nin_verified": current_user.nin_verified,
        "bvn_verified": current_user.bvn_verified,
        "is_verified": current_user.is_verified,
        "verification_level": (
            "full" if current_user.nin_verified and current_user.bvn_verified
            else "partial" if current_user.nin_verified or current_user.bvn_verified
            else "none"
        )
    }

