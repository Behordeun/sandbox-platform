from typing import Any
from app.services.discovery import service_discovery
from app.services.health import health_service
from app.services.proxy import proxy_service
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response

router = APIRouter()

# Auth service proxy routes
@router.get("/auth/{path:path}")
async def proxy_auth_get(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "auth", f"/api/v1/auth/{path}")

@router.post("/auth/{path:path}")
async def proxy_auth_post(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "auth", f"/api/v1/auth/{path}")

@router.put("/auth/{path:path}")
async def proxy_auth_put(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "auth", f"/api/v1/auth/{path}")

@router.delete("/auth/{path:path}")
async def proxy_auth_delete(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "auth", f"/api/v1/auth/{path}")

@router.patch("/auth/{path:path}")
async def proxy_auth_patch(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "auth", f"/api/v1/auth/{path}")

# NIN service proxy routes
@router.get("/nin/{path:path}")
async def proxy_nin_get(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "nin", f"/api/v1/nin/{path}")

@router.post("/nin/{path:path}")
async def proxy_nin_post(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "nin", f"/api/v1/nin/{path}")

# BVN service proxy routes
@router.get("/bvn/{path:path}")
async def proxy_bvn_get(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "bvn", f"/api/v1/bvn/{path}")

@router.post("/bvn/{path:path}")
async def proxy_bvn_post(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "bvn", f"/api/v1/bvn/{path}")

# SMS service proxy routes
@router.get("/sms/{path:path}")
async def proxy_sms_get(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "sms", f"/api/v1/sms/{path}")

@router.post("/sms/{path:path}")
async def proxy_sms_post(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "sms", f"/api/v1/sms/{path}")

# AI service proxy routes
@router.get("/llm/{path:path}")
async def proxy_ai_get(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "ai", f"/api/v1/ai/{path}")

@router.post("/llm/{path:path}")
async def proxy_ai_post(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "ai", f"/api/v1/ai/{path}")

# Health endpoints
@router.get("/services/health")
async def get_services_health() -> Any:
    return await health_service.get_services_health()

@router.get("/dpi/health")
async def get_dpi_health() -> Any:
    dpi_services = ["nin", "bvn", "sms", "ai"]
    health_status = await health_service.get_services_health()
    
    return {
        "status": "healthy" if health_status.get("overall_status") == "healthy" else "degraded",
        "services": {k: v for k, v in health_status.get("services", {}).items() if k in dpi_services},
        "ready_for_development": all(
            health_status.get("services", {}).get(svc, {}).get("status") == "healthy"
            for svc in dpi_services
        ),
    }

@router.get("/services/{service_name}/health")
async def get_service_health(service_name: str) -> Any:
    result = await proxy_service.health_check_service(service_name)
    if result["status"] == "unknown":
        raise HTTPException(status_code=404, detail="Service not found")
    return result