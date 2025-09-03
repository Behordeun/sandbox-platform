from typing import Any

from fastapi import APIRouter

router = APIRouter()


@router.get("/nin", tags=["examples"])
async def nin_examples() -> Any:
    """📋 NIN Verification Examples"""
    return {
        "success": True,
        "message": "NIN verification examples",
        "data": {
            "test_nin": "12345678901",
            "example_request": {"nin": "12345678901"},
            "example_response": {
                "success": True,
                "message": "NIN verified successfully",
                "data": {
                    "nin": "12345678901",
                    "first_name": "Adebayo",
                    "last_name": "Ogundimu",
                    "date_of_birth": "1990-01-15",
                    "gender": "Male",
                },
            },
        },
    }


@router.get("/sms", tags=["examples"])
async def sms_examples() -> Any:
    """📱 Nigerian SMS Examples"""
    return {
        "success": True,
        "message": "SMS examples",
        "data": {
            "example_request": {
                "to": "+2348012345678",
                "message": "Your OTP is 123456. Valid for 5 minutes.",
            },
            "bulk_sms_request": {
                "recipients": ["+2348012345678", "+2347012345678"],
                "message": "Welcome to our DPI platform!",
            },
        },
    }


@router.get("/auth", tags=["examples"])
async def auth_examples() -> Any:
    """🔐 OAuth2 Bearer Token Examples"""
    return {
        "success": True,
        "message": "OAuth2 Bearer Token authentication examples",
        "data": {
            "step_1_login": {
                "method": "POST",
                "url": "/api/v1/auth/login",
                "headers": {"Content-Type": "application/json"},
                "body": {
                    "identifier": "startup@fintech.ng",
                    "password": "your-password",
                },
                "response": {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 3600,
                    "user": {
                        "id": 1,
                        "email": "startup@fintech.ng",
                        "username": "startup_dev",
                    },
                },
            },
            "step_2_use_token": {
                "method": "POST",
                "url": "/api/v1/nin/verify",
                "headers": {
                    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "Content-Type": "application/json",
                },
                "body": {"nin": "12345678901"},
                "note": "Replace the token with your actual access_token from step 1",
            },
            "curl_examples": {
                "login": 'curl -X POST http://localhost:8080/api/v1/auth/login -H \'Content-Type: application/json\' -d \'{"identifier": "startup@fintech.ng", "password": "your-password"}\'',
                "verify_nin": "curl -X POST http://localhost:8080/api/v1/nin/verify -H 'Authorization: Bearer YOUR_TOKEN' -H 'Content-Type: application/json' -d '{\"nin\": \"12345678901\"}'",
                "send_sms": 'curl -X POST http://localhost:8080/api/v1/sms/send -H \'Authorization: Bearer YOUR_TOKEN\' -H \'Content-Type: application/json\' -d \'{"to": "+2348012345678", "message": "Your OTP is 123456"}\'',
            },
        },
    }


@router.get("/integration", tags=["examples"])
async def integration_examples() -> Any:
    """🚀 Complete DPI Integration Examples"""
    return {
        "success": True,
        "message": "Complete DPI integration workflow",
        "data": {
            "workflow": {
                "1_authenticate": {
                    "description": "Get bearer token for API access",
                    "endpoint": "POST /api/v1/auth/login",
                    "required": True,
                },
                "2_verify_identity": {
                    "description": "Verify user NIN or BVN for KYC",
                    "endpoints": ["POST /api/v1/nin/verify", "POST /api/v1/bvn/verify"],
                    "requires_token": True,
                },
                "3_send_notification": {
                    "description": "Send SMS notifications to users",
                    "endpoint": "POST /api/v1/sms/send",
                    "requires_token": True,
                },
                "4_ai_assistance": {
                    "description": "Generate Nigerian-context content",
                    "endpoint": "POST /api/v1/ai/chat",
                    "requires_token": True,
                },
            }
        },
    }
