import httpx
from app.core.config import settings
from fastapi import HTTPException


async def verify_nin_with_doja(nin: str) -> dict:
    """Verify NIN using Dojah API."""
    if not settings.doja_api_key:
        raise HTTPException(
            status_code=500, detail="NIN verification service not configured"
        )

    headers = {
        "Authorization": f"Bearer {settings.doja_api_key}",
        "AppId": settings.doja_app_id,
        "Content-Type": "application/json",
    }

    payload = {"nin": nin}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.doja_base_url}/api/v1/kyc/nin",
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
                        "first_name": entity.get("firstname"),
                        "last_name": entity.get("lastname"),
                        "middle_name": entity.get("middlename"),
                        "date_of_birth": entity.get("birthdate"),
                        "gender": entity.get("gender"),
                        "phone_number": entity.get("telephoneno"),
                        "email": entity.get("email"),
                        "address": entity.get("residence_AdressLine1"),
                        "state_of_origin": entity.get("residence_state"),
                        "lga_of_origin": entity.get("residence_lga"),
                        "nin": entity.get("nin"),
                        "photo": entity.get("photo"),
                    },
                    "message": "NIN verified successfully",
                }
            else:
                error_msg = response_data.get("error", {}).get("message", "Verification failed")
                return {
                    "success": False,
                    "data": None,
                    "message": f"NIN verification failed: {error_msg}",
                }
        except httpx.TimeoutException:
            return {
                "success": False,
                "data": None,
                "message": "NIN verification service timeout",
            }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "message": f"NIN verification error: {str(e)}",
            }