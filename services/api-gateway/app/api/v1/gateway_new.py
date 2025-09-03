import sys
from pathlib import Path
from typing import Any

# Add service paths to Python path for imports
sandbox_path = Path(__file__).parent.parent.parent.parent.parent / "sandbox"
services_path = Path(__file__).parent.parent.parent.parent.parent / "services"
sys.path.insert(0, str(sandbox_path))
sys.path.insert(0, str(services_path))

from app.services.discovery import service_discovery
from app.services.health import health_service
from app.services.proxy import proxy_service
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response

# Import actual service routers
try:
    from nin.app.api.v1.router import api_router as nin_router
except ImportError:
    nin_router = None

try:
    from bvn.app.api.v1.router import api_router as bvn_router
except ImportError:
    bvn_router = None

try:
    from ai.app.api.v1.router import api_router as ai_router
except ImportError:
    ai_router = None

try:
    from auth_service.app.api.v1.auth import router as auth_router
    from auth_service.app.api.v1.admin import router as admin_router
    from auth_service.app.api.v1.oauth import router as oauth_router
except ImportError:
    auth_router = None
    admin_router = None
    oauth_router = None

router = APIRouter()

# Include actual service routers with proper prefixes
if auth_router:
    router.include_router(auth_router, prefix="/auth", tags=["auth"])
if admin_router:
    router.include_router(admin_router, prefix="/auth/admin", tags=["admin"])
if oauth_router:
    router.include_router(oauth_router, prefix="/auth/oauth2", tags=["oauth"])
if nin_router:
    router.include_router(nin_router, prefix="/nin", tags=["nin"])
if bvn_router:
    router.include_router(bvn_router, prefix="/bvn", tags=["bvn"])
if ai_router:
    router.include_router(ai_router, prefix="/llm", tags=["ai"])

# Fallback proxy routes for services not directly imported
@router.get("/sms/{path:path}")
async def proxy_sms_get(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "sms", f"/api/v1/sms/{path}")

@router.post("/sms/{path:path}")
async def proxy_sms_post(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "sms", f"/api/v1/sms/{path}")

@router.put("/sms/{path:path}")
async def proxy_sms_put(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "sms", f"/api/v1/sms/{path}")

@router.delete("/sms/{path:path}")
async def proxy_sms_delete(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "sms", f"/api/v1/sms/{path}")

# Health and status endpoints
@router.get("/services/health")
async def get_services_health() -> Any:
    return await health_service.get_services_health()

@router.get("/dpi/health")
async def get_dpi_health() -> Any:
    dpi_services = ["nin", "bvn", "sms", "llm"]
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

@router.get("/services/{service_name}/health")
async def get_service_health(service_name: str) -> Any:
    result = await proxy_service.health_check_service(service_name)
    if result["status"] == "unknown":
        raise HTTPException(status_code=404, detail="Service not found")
    return result