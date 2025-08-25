from typing import Any

from app.services.discovery import service_discovery
from app.services.health import health_service
from app.services.proxy import proxy_service
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response

router = APIRouter()


@router.api_route(
    "/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    operation_id="proxy_auth_service_{method}"
)
async def proxy_auth_service(request: Request, path: str) -> Response:
    """Proxy requests to auth service."""
    return await proxy_service.proxy_request(request, "auth", f"/{path}")


@router.api_route(
    "/sms/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    operation_id="proxy_sms_service_{method}"
)
async def proxy_sms_service(request: Request, path: str) -> Response:
    """Proxy requests to SMS service."""
    return await proxy_service.proxy_request(request, "sms", f"/{path}")


@router.api_route(
    "/llm/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    operation_id="proxy_llm_service_{method}"
)
async def proxy_llm_service(request: Request, path: str) -> Response:
    """Proxy requests to LLM service."""
    return await proxy_service.proxy_request(request, "llm", f"/{path}")


@router.api_route(
    "/nin/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    operation_id="proxy_nin_service_{method}"
)
async def proxy_nin_service(request: Request, path: str) -> Response:
    """Proxy requests to NIN service."""
    return await proxy_service.proxy_request(request, "nin", f"/{path}")


@router.api_route(
    "/bvn/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    operation_id="proxy_bvn_service_{method}"
)
async def proxy_bvn_service(request: Request, path: str) -> Response:
    """Proxy requests to BVN service."""
    return await proxy_service.proxy_request(request, "bvn", f"/{path}")


@router.get("/services/health")
async def get_services_health() -> Any:
    """Get health status of all backend services."""
    return await health_service.get_services_health()


@router.get("/dpi/health")
async def get_dpi_health() -> Any:
    """Get DPI-specific service health for developers."""
    dpi_services = ["nin", "bvn", "sms", "llm"]
    health_status = await health_service.get_services_health()
    
    dpi_health = {
        "status": "healthy" if health_status.get("overall_status") == "healthy" else "degraded",
        "services": {k: v for k, v in health_status.get("services", {}).items() if k in dpi_services},
        "ready_for_development": all(
            health_status.get("services", {}).get(svc, {}).get("status") == "healthy" 
            for svc in dpi_services
        )
    }
    return dpi_health


@router.get("/services/status")
async def get_services_status() -> Any:
    """Get detailed status of all services."""
    return service_discovery.get_service_status()


@router.get("/services/{service_name}/health")
async def get_service_health(service_name: str) -> Any:
    """Get health status of a specific service."""
    result = await proxy_service.health_check_service(service_name)
    if result["status"] == "unknown":
        raise HTTPException(status_code=404, detail="Service not found")
    return result


@router.get("/services/{service_name}/metrics")
async def get_service_metrics(service_name: str) -> Any:
    """Get metrics for a specific service."""
    return health_service.get_service_metrics(service_name)


@router.post("/auth/login")
async def system_login(request: Request) -> Response:
    """System-wide authentication endpoint.
    
    Example for Nigerian developers:
    {
        "identifier": "developer@fintech.ng",
        "password": "SecurePass123"
    }
    """
    return await proxy_service.proxy_request(request, "auth", "/api/v1/auth/login/json")


@router.get("/examples/nin")
async def nin_examples():
    """NIN verification examples for Nigerian developers"""
    return {
        "success": True,
        "message": "NIN verification examples",
        "data": {
            "test_nin": "12345678901",
            "example_request": {
                "nin": "12345678901"
            },
            "example_response": {
                "success": True,
                "message": "NIN verified successfully",
                "data": {
                    "nin": "12345678901",
                    "first_name": "Adebayo",
                    "last_name": "Ogundimu",
                    "date_of_birth": "1990-01-15",
                    "gender": "Male"
                }
            }
        }
    }


@router.get("/examples/sms")
async def sms_examples():
    """SMS examples for Nigerian developers"""
    return {
        "success": True,
        "message": "SMS examples",
        "data": {
            "example_request": {
                "to": "+2348012345678",
                "message": "Your OTP is 123456. Valid for 5 minutes."
            },
            "bulk_sms_request": {
                "recipients": ["+2348012345678", "+2347012345678"],
                "message": "Welcome to our DPI platform!"
            }
        }
    }
