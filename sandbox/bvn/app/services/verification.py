import httpx
from app.core.yaml_config import settings
from fastapi import HTTPException


async def verify_bvn_with_doja(bvn: str) -> dict:
    """Verify BVN using Dojah API."""
    if not settings.doja_api_key:
        raise HTTPException(
            status_code=500, detail="BVN verification service not configured"
        )

    headers = {
        "Authorization": f"Bearer {settings.doja_api_key}",
        "AppId": settings.doja_app_id,
        "Content-Type": "application/json",
    }

    payload = {"bvn": bvn}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.doja_base_url}/api/v1/kyc/bvn",
                json=payload,
                headers=headers,
                timeout=30.0,
            )

            response_data = response.json()

            if response.status_code == 200 and response_data.get("success"):
                entity = response_data.get("entity", {})
                return {
                    "success": True,
                    "data": {
                        "first_name": entity.get("first_name"),
                        "last_name": entity.get("last_name"),
                        "middle_name": entity.get("middle_name"),
                        "date_of_birth": entity.get("date_of_birth"),
                        "gender": entity.get("gender"),
                        "phone_number": entity.get("phone_number1"),
                        "email": entity.get("email"),
                        "address": entity.get("residential_address"),
                        "state_of_origin": entity.get("state_of_origin"),
                        "lga_of_origin": entity.get("lga_of_origin"),
                        "bvn": entity.get("bvn"),
                        "enrollment_bank": entity.get("enrollment_bank"),
                        "enrollment_branch": entity.get("enrollment_branch"),
                        "watch_listed": entity.get("watch_listed"),
                    },
                    "message": "BVN verified successfully",
                }
            else:
                error_msg = response_data.get("error", {}).get(
                    "message", "Verification failed"
                )
                return {
                    "success": False,
                    "data": None,
                    "message": f"BVN verification failed: {error_msg}",
                }
        except httpx.TimeoutException:
            return {
                "success": False,
                "data": None,
                "message": "BVN verification service timeout",
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"BVN verification error: {str(e)}",
            }
