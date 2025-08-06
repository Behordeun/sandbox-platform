from typing import Any

from app.services.discovery import service_discovery
from app.services.health import health_service
from app.services.proxy import proxy_service
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response

router = APIRouter()


@router.api_route(
    "/auth/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
)
async def proxy_auth_service(request: Request, path: str) -> Response:
    """Proxy requests to auth service."""
    return await proxy_service.proxy_request(request, "auth", f"/{path}")


@router.api_route(
    "/sms/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
)
async def proxy_sms_service(request: Request, path: str) -> Response:
    """Proxy requests to SMS service."""
    return await proxy_service.proxy_request(request, "sms", f"/{path}")


@router.api_route(
    "/llm/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
)
async def proxy_llm_service(request: Request, path: str) -> Response:
    """Proxy requests to LLM service."""
    return await proxy_service.proxy_request(request, "llm", f"/{path}")


@router.get("/services/health")
async def get_services_health() -> Any:
    """Get health status of all backend services."""
    return await health_service.get_services_health()


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
