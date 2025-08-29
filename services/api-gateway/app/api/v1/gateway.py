from typing import Any

from app.services.discovery import service_discovery
from app.services.health import health_service
from app.services.proxy import proxy_service
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel

router = APIRouter()


def _auth_upstream(path: str) -> str:
    return f"/api/v1/auth/{path}" if path else "/api/v1/auth"


@router.get("/auth/{path:path}", operation_id="proxy_auth_service_get")
async def proxy_auth_get(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "auth", _auth_upstream(path))


@router.post("/auth/{path:path}", operation_id="proxy_auth_service_post")
async def proxy_auth_post(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "auth", _auth_upstream(path))


@router.put("/auth/{path:path}", operation_id="proxy_auth_service_put")
async def proxy_auth_put(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "auth", _auth_upstream(path))


@router.delete("/auth/{path:path}", operation_id="proxy_auth_service_delete")
async def proxy_auth_delete(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "auth", _auth_upstream(path))


@router.patch("/auth/{path:path}", operation_id="proxy_auth_service_patch")
async def proxy_auth_patch(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "auth", _auth_upstream(path))


@router.options("/auth/{path:path}", operation_id="proxy_auth_service_options")
async def proxy_auth_options(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "auth", _auth_upstream(path))


def _sms_upstream(path: str) -> str:
    return f"/api/v1/sms/{path}" if path else "/api/v1/sms"


@router.get("/sms/{path:path}", operation_id="proxy_sms_service_get")
async def proxy_sms_get(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "sms", _sms_upstream(path))


@router.post("/sms/{path:path}", operation_id="proxy_sms_service_post")
async def proxy_sms_post(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "sms", _sms_upstream(path))


@router.put("/sms/{path:path}", operation_id="proxy_sms_service_put")
async def proxy_sms_put(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "sms", _sms_upstream(path))


@router.delete("/sms/{path:path}", operation_id="proxy_sms_service_delete")
async def proxy_sms_delete(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "sms", _sms_upstream(path))


@router.patch("/sms/{path:path}", operation_id="proxy_sms_service_patch")
async def proxy_sms_patch(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "sms", _sms_upstream(path))


@router.options("/sms/{path:path}", operation_id="proxy_sms_service_options")
async def proxy_sms_options(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "sms", _sms_upstream(path))


def _llm_upstream(path: str) -> str:
    return f"/api/v1/ai/{path}" if path else "/api/v1/ai"


@router.get("/llm/{path:path}", operation_id="proxy_llm_service_get")
async def proxy_llm_get(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "ai", _llm_upstream(path))


@router.post("/llm/{path:path}", operation_id="proxy_llm_service_post")
async def proxy_llm_post(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "ai", _llm_upstream(path))


@router.put("/llm/{path:path}", operation_id="proxy_llm_service_put")
async def proxy_llm_put(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "ai", _llm_upstream(path))


@router.delete("/llm/{path:path}", operation_id="proxy_llm_service_delete")
async def proxy_llm_delete(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "ai", _llm_upstream(path))


@router.patch("/llm/{path:path}", operation_id="proxy_llm_service_patch")
async def proxy_llm_patch(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "ai", _llm_upstream(path))


@router.options("/llm/{path:path}", operation_id="proxy_llm_service_options")
async def proxy_llm_options(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "ai", _llm_upstream(path))


def _nin_upstream(path: str) -> str:
    return f"/api/v1/nin/{path}" if path else "/api/v1/nin"


@router.get("/nin/{path:path}", operation_id="proxy_nin_service_get")
async def proxy_nin_get(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "nin", _nin_upstream(path))


@router.post("/nin/{path:path}", operation_id="proxy_nin_service_post")
async def proxy_nin_post(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "nin", _nin_upstream(path))


@router.put("/nin/{path:path}", operation_id="proxy_nin_service_put")
async def proxy_nin_put(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "nin", _nin_upstream(path))


@router.delete("/nin/{path:path}", operation_id="proxy_nin_service_delete")
async def proxy_nin_delete(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "nin", _nin_upstream(path))


@router.patch("/nin/{path:path}", operation_id="proxy_nin_service_patch")
async def proxy_nin_patch(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "nin", _nin_upstream(path))


@router.options("/nin/{path:path}", operation_id="proxy_nin_service_options")
async def proxy_nin_options(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "nin", _nin_upstream(path))


def _bvn_upstream(path: str) -> str:
    return f"/api/v1/bvn/{path}" if path else "/api/v1/bvn"


@router.get("/bvn/{path:path}", operation_id="proxy_bvn_service_get")
async def proxy_bvn_get(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "bvn", _bvn_upstream(path))


@router.post("/bvn/{path:path}", operation_id="proxy_bvn_service_post")
async def proxy_bvn_post(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "bvn", _bvn_upstream(path))


@router.put("/bvn/{path:path}", operation_id="proxy_bvn_service_put")
async def proxy_bvn_put(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "bvn", _bvn_upstream(path))


@router.delete("/bvn/{path:path}", operation_id="proxy_bvn_service_delete")
async def proxy_bvn_delete(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "bvn", _bvn_upstream(path))


@router.patch("/bvn/{path:path}", operation_id="proxy_bvn_service_patch")
async def proxy_bvn_patch(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "bvn", _bvn_upstream(path))


@router.options("/bvn/{path:path}", operation_id="proxy_bvn_service_options")
async def proxy_bvn_options(request: Request, path: str) -> Response:
    return await proxy_service.proxy_request(request, "bvn", _bvn_upstream(path))


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


class LoginRequest(BaseModel):
    identifier: str
    password: str


## (moved system_login above catch-all routes for precedence)


@router.get("/examples/nin")
async def nin_examples():
    """NIN verification examples for Nigerian developers"""
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


@router.get("/examples/sms")
async def sms_examples():
    """SMS examples for Nigerian developers"""
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
class LoginRequest(BaseModel):
    identifier: str
    password: str


@router.post(
    "/auth/login",
    tags=["gateway"],
    operation_id="system_login",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "title": "LoginRequest",
                        "type": "object",
                        "properties": {
                            "identifier": {"type": "string"},
                            "password": {"type": "string"},
                        },
                        "required": ["identifier", "password"],
                    }
                },
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "username": {"type": "string"},
                            "password": {"type": "string"},
                        },
                        "required": ["username", "password"],
                    }
                },
            },
        }
    },
)
async def system_login(request: Request) -> Response:
    """System-wide authentication endpoint accepting JSON or form data.

    Accepts:
    - application/json: {"identifier": "...", "password": "..."}
    - application/x-www-form-urlencoded: username=...&password=...
    """
    content_type = request.headers.get("content-type", "").lower()
    data = await parse_login_payload(request, content_type)
    identifier, password, details = validate_login_payload(data)

    if not identifier or not password:
        return JSONResponse(status_code=422, content={"detail": details})

    return await proxy_service.proxy_request(
        request,
        "auth",
        "/api/v1/auth/login/json",
        json_payload={"identifier": identifier, "password": password},
    )


async def parse_login_payload(request: Request, content_type: str):
    try:
        if "application/json" in content_type:
            data = await request.json()
        else:
            form = await request.form()
            data = dict(form) if form is not None else None
    except Exception:
        data = None
    return data


def validate_login_payload(data):
    identifier = None
    password = None
    if isinstance(data, dict):
        identifier = data.get("identifier") or data.get("username")
        password = data.get("password")
    details = []
    if not (data and ("identifier" in data or "username" in data)):
        details.append({
            "type": "missing",
            "loc": ["body", "identifier|username"],
            "msg": "Field required",
            "input": None,
        })
    if not (data and "password" in data):
        details.append({
            "type": "missing",
            "loc": ["body", "password"],
            "msg": "Field required",
            "input": None,
        })
    return identifier, password, details
