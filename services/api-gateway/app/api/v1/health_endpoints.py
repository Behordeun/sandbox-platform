from typing import Any

from app.services.client import service_client
from app.services.health import health_service
from fastapi import APIRouter, Request

router = APIRouter()


@router.get("/services/health", tags=["health"])
async def get_services_health() -> Any:
    """
    💚 Platform Health Overview

    Comprehensive health check for all backend services.
    Essential for monitoring Nigerian DPI platform status.
    """
    return await health_service.get_services_health()


@router.get("/dpi/health", tags=["health"])
async def get_dpi_health() -> Any:
    """
    🇳🇬 Nigerian DPI Services Health

    Focused health check for core DPI services.
    Tailored for Nigerian startup developers.
    """
    dpi_services = ["nin", "bvn", "sms", "ai"]
    health_status = await health_service.get_services_health()

    dpi_health = {
        "status": (
            "healthy"
            if health_status.get("overall_status") == "healthy"
            else "degraded"
        ),
        "services": {
            k: v
            for k, v in health_status.get("services", {}).items()
            if k in dpi_services
        },
        "ready_for_development": all(
            health_status.get("services", {}).get(svc, {}).get("status") == "healthy"
            for svc in dpi_services
        ),
    }
    return dpi_health


@router.get("/services/{service_name}/health", tags=["health"])
async def get_service_health(request: Request, service_name: str) -> Any:
    """
    🔍 Individual Service Health

    Detailed health check for a specific service.
    Essential for troubleshooting and monitoring.
    """
    return await service_client.make_request(
        request=request,
        service_name=service_name,
        method="GET",
        path="/health",
    )


@router.get("/services/{service_name}/metrics", tags=["health"])
async def get_service_metrics(service_name: str) -> Any:
    """
    📈 Service Performance Metrics

    Detailed performance and usage metrics for specific service.
    Critical for capacity planning and optimization.
    """
    return health_service.get_service_metrics(service_name)
