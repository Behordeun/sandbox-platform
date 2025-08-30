from typing import Any

from app.services.discovery import service_discovery
from app.services.health import health_service
from app.services.proxy import proxy_service
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, Response

router = APIRouter()


# Specific system login endpoint MUST be declared before catch-all /auth/{path}
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
        details.append(
            {
                "type": "missing",
                "loc": ["body", "identifier|username"],
                "msg": "Field required",
                "input": None,
            }
        )
    if not (data and "password" in data):
        details.append(
            {
                "type": "missing",
                "loc": ["body", "password"],
                "msg": "Field required",
                "input": None,
            }
        )
    return identifier, password, details


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
    """
    🚪 Universal Login Gateway
    
    Primary authentication endpoint for Nigerian DPI platform.
    Accepts both JSON and form data for maximum compatibility.
    
    **Supported Formats:**
    - JSON: {"identifier": "user@fintech.ng", "password": "pass"}
    - Form: username=user&password=pass
    
    **Features:**
    - ✅ Email or username login
    - ✅ OAuth2 form compatibility
    - ✅ JSON API compatibility
    - ✅ Request correlation tracking
    
    **Nigerian Context:** Optimized for fintech and DPI applications
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


def _auth_upstream(path: str) -> str:
    return f"/api/v1/auth/{path}" if path else "/api/v1/auth"


@router.get("/auth/{path:path}", operation_id="proxy_auth_service_get")
async def proxy_auth_get(request: Request, path: str) -> Response:
    """
    🔐 Auth Service GET Proxy
    
    Route GET requests to authentication service.
    Handles user profile, admin endpoints, and OAuth flows.
    
    **Common Paths:**
    - /auth/me - Get current user profile
    - /auth/admin/users - List users (admin only)
    - /auth/oauth2/clients - OAuth client management
    
    **Features:**
    - ✅ Request correlation tracking
    - ✅ Authentication header forwarding
    - ✅ Error handling and logging
    """
    return await proxy_service.proxy_request(request, "auth", _auth_upstream(path))


@router.post("/auth/{path:path}", operation_id="proxy_auth_service_post")
async def proxy_auth_post(request: Request, path: str) -> Response:
    """
    🔐 Auth Service POST Proxy
    
    Route POST requests to authentication service.
    Handles login, user creation, and admin operations.
    
    **Common Paths:**
    - /auth/login/json - JSON login endpoint
    - /auth/logout - User logout
    - /auth/admin/users - Create user (admin only)
    - /auth/oauth2/token - OAuth token exchange
    
    **Nigerian Context:** Optimized for fintech authentication flows
    """
    return await proxy_service.proxy_request(request, "auth", _auth_upstream(path))


@router.put("/auth/{path:path}", operation_id="proxy_auth_service_put")
async def proxy_auth_put(request: Request, path: str) -> Response:
    """
    🔐 Auth Service PUT Proxy
    
    Route PUT requests to authentication service.
    Handles user profile updates and admin modifications.
    
    **Common Paths:**
    - /auth/admin/users/{id} - Update user profile
    - /auth/oauth2/clients/{id} - Update OAuth client
    
    **Features:**
    - ✅ Profile data validation
    - ✅ Admin permission checks
    - ✅ Audit trail logging
    """
    return await proxy_service.proxy_request(request, "auth", _auth_upstream(path))


@router.delete("/auth/{path:path}", operation_id="proxy_auth_service_delete")
async def proxy_auth_delete(request: Request, path: str) -> Response:
    """
    🔐 Auth Service DELETE Proxy
    
    Route DELETE requests to authentication service.
    Handles user account deletion and cleanup operations.
    
    **Common Paths:**
    - /auth/admin/users/{id} - Soft delete user account
    - /auth/oauth2/clients/{id} - Remove OAuth client
    
    **Security:**
    - ✅ Soft delete for compliance
    - ✅ Admin-only access
    - ✅ NDPR compliant data handling
    """
    return await proxy_service.proxy_request(request, "auth", _auth_upstream(path))


@router.patch("/auth/{path:path}", operation_id="proxy_auth_service_patch")
async def proxy_auth_patch(request: Request, path: str) -> Response:
    """
    🔐 Auth Service PATCH Proxy
    
    Route PATCH requests to authentication service.
    Handles partial updates and status changes.
    
    **Common Paths:**
    - /auth/admin/users/{id}/activate - Activate user
    - /auth/admin/users/{id}/deactivate - Deactivate user
    - /auth/admin/users/{id}/reset-password - Reset password
    
    **Use Cases:**
    - Account status management
    - Partial profile updates
    - Administrative actions
    """
    return await proxy_service.proxy_request(request, "auth", _auth_upstream(path))


@router.options("/auth/{path:path}", operation_id="proxy_auth_service_options")
async def proxy_auth_options(request: Request, path: str) -> Response:
    """
    🔐 Auth Service OPTIONS Proxy
    
    Handle CORS preflight requests for authentication service.
    Essential for web application integration.
    
    **CORS Support:**
    - ✅ Preflight request handling
    - ✅ Nigerian domain support (.ng, .com.ng)
    - ✅ Fintech application compatibility
    
    **Headers:** Returns allowed methods and CORS policies
    """
    return await proxy_service.proxy_request(request, "auth", _auth_upstream(path))


def _sms_upstream(path: str) -> str:
    return f"/api/v1/sms/{path}" if path else "/api/v1/sms"


@router.get("/sms/{path:path}", operation_id="proxy_sms_service_get")
async def proxy_sms_get(request: Request, path: str) -> Response:
    """
    📱 SMS Service GET Proxy
    
    Route GET requests to Nigerian SMS service.
    Retrieve message status, delivery reports, and service info.
    
    **Common Paths:**
    - /sms/status/{message_id} - Check message delivery
    - /sms/balance - Check SMS credit balance
    - /sms/templates - Get message templates
    
    **Nigerian Networks:** MTN, Airtel, Glo, 9mobile support
    """
    return await proxy_service.proxy_request(request, "sms", _sms_upstream(path))


@router.post("/sms/{path:path}", operation_id="proxy_sms_service_post")
async def proxy_sms_post(request: Request, path: str) -> Response:
    """
    📱 SMS Service POST Proxy
    
    Route POST requests to Nigerian SMS service.
    Send SMS messages, OTP codes, and bulk notifications.
    
    **Common Paths:**
    - /sms/send - Send single SMS
    - /sms/bulk - Send bulk SMS
    - /sms/otp/generate - Generate OTP code
    - /sms/otp/verify - Verify OTP code
    
    **Features:**
    - ✅ Nigerian phone number validation
    - ✅ Network-optimized routing
    - ✅ Delivery confirmation
    - ✅ Cost optimization
    """
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
    """
    🤖 AI/LLM Service GET Proxy
    
    Route GET requests to Nigerian-context AI service.
    Retrieve conversation history, model info, and analytics.
    
    **Common Paths:**
    - /llm/models - Available AI models
    - /llm/conversations/{id} - Get conversation
    - /llm/usage - Token usage statistics
    
    **Nigerian Context:**
    - ✅ Local language support (Yoruba, Igbo, Hausa)
    - ✅ Fintech terminology understanding
    - ✅ Cultural context awareness
    """
    return await proxy_service.proxy_request(request, "ai", _llm_upstream(path))


@router.post("/llm/{path:path}", operation_id="proxy_llm_service_post")
async def proxy_llm_post(request: Request, path: str) -> Response:
    """
    🤖 AI/LLM Service POST Proxy
    
    Route POST requests to Nigerian-context AI service.
    Generate content, analyze text, and process conversations.
    
    **Common Paths:**
    - /llm/chat - Interactive chat completion
    - /llm/generate - Content generation
    - /llm/analyze - Text analysis
    - /llm/translate - Nigerian language translation
    
    **Capabilities:**
    - ✅ Nigerian financial terminology
    - ✅ Multi-language support
    - ✅ Context-aware responses
    - ✅ Compliance-friendly content
    """
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
    """
    🇳🇬 NIN Service GET Proxy
    
    Route GET requests to Nigerian Identity Number service.
    Check verification status and retrieve identity data.
    
    **Common Paths:**
    - /nin/status/{nin} - Check NIN verification status
    - /nin/verify/{request_id} - Get verification result
    - /nin/statistics - Service usage statistics
    
    **NIMC Integration:**
    - ✅ Real-time NIN validation
    - ✅ Dojah API integration
    - ✅ Privacy-compliant data handling
    - ✅ Audit trail maintenance
    """
    return await proxy_service.proxy_request(request, "nin", _nin_upstream(path))


@router.post("/nin/{path:path}", operation_id="proxy_nin_service_post")
async def proxy_nin_post(request: Request, path: str) -> Response:
    """
    🇳🇬 NIN Service POST Proxy
    
    Route POST requests to Nigerian Identity Number service.
    Initiate NIN verification and identity validation.
    
    **Common Paths:**
    - /nin/verify - Verify NIN with NIMC
    - /nin/lookup - Basic NIN information lookup
    - /nin/batch - Bulk NIN verification
    
    **Verification Process:**
    1. NIN format validation
    2. NIMC database query via Dojah
    3. Identity data extraction
    4. Privacy-compliant response
    
    **Compliance:** NDPR and KYC regulation compliant
    """
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
    """
    🇳🇬 BVN Service GET Proxy
    
    Route GET requests to Bank Verification Number service.
    Check BVN status and retrieve banking identity data.
    
    **Common Paths:**
    - /bvn/status/{bvn} - Check BVN verification status
    - /bvn/verify/{request_id} - Get verification result
    - /bvn/banks - Supported Nigerian banks
    
    **CBN Integration:**
    - ✅ Real-time BVN validation
    - ✅ Nigerian bank network access
    - ✅ Financial identity verification
    - ✅ Regulatory compliance
    """
    return await proxy_service.proxy_request(request, "bvn", _bvn_upstream(path))


@router.post("/bvn/{path:path}", operation_id="proxy_bvn_service_post")
async def proxy_bvn_post(request: Request, path: str) -> Response:
    """
    🇳🇬 BVN Service POST Proxy
    
    Route POST requests to Bank Verification Number service.
    Initiate BVN verification and financial identity validation.
    
    **Common Paths:**
    - /bvn/verify - Verify BVN with CBN
    - /bvn/lookup - Basic BVN information lookup
    - /bvn/match - Match BVN with user data
    
    **Verification Features:**
    - ✅ 11-digit BVN validation
    - ✅ Nigerian banking system integration
    - ✅ Financial KYC compliance
    - ✅ Anti-fraud protection
    
    **Fintech Ready:** Optimized for Nigerian fintech applications
    """
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
    """
    💚 Platform Health Overview
    
    Comprehensive health check for all backend services.
    Essential for monitoring Nigerian DPI platform status.
    
    **Returns:**
    - Overall platform status
    - Individual service health
    - Response times and availability
    - Database connectivity status
    
    **Use Cases:**
    - Platform monitoring dashboards
    - Startup integration health checks
    - DevOps service discovery
    """
    return await health_service.get_services_health()


@router.get("/dpi/health")
async def get_dpi_health() -> Any:
    """
    🇳🇬 Nigerian DPI Services Health
    
    Focused health check for core DPI services.
    Tailored for Nigerian startup developers.
    
    **DPI Services Monitored:**
    - NIN verification service
    - BVN validation service  
    - SMS messaging service
    - AI/LLM service
    
    **Response Includes:**
    - ready_for_development: Boolean status
    - Individual service availability
    - Development environment readiness
    """
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
    """
    📊 Detailed Service Status
    
    Comprehensive status report for all platform services.
    Includes performance metrics and availability data.
    
    **Status Information:**
    - Service discovery registry
    - Response time metrics
    - Error rate statistics
    - Resource utilization
    
    **DevOps Integration:**
    - ✅ Kubernetes health checks
    - ✅ Load balancer status
    - ✅ Database connectivity
    - ✅ External API dependencies
    """
    return service_discovery.get_service_status()


@router.get("/services/{service_name}/health")
async def get_service_health(service_name: str) -> Any:
    """
    🔍 Individual Service Health
    
    Detailed health check for a specific service.
    Essential for troubleshooting and monitoring.
    
    **Supported Services:**
    - auth: Authentication service
    - sms: Nigerian SMS service
    - nin: NIN verification service
    - bvn: BVN validation service
    - ai: AI/LLM service
    
    **Health Metrics:**
    - ✅ Service availability
    - ✅ Response time
    - ✅ Database connectivity
    - ✅ External API status
    """
    result = await proxy_service.health_check_service(service_name)
    if result["status"] == "unknown":
        raise HTTPException(status_code=404, detail="Service not found")
    return result


@router.get("/services/{service_name}/metrics")
async def get_service_metrics(service_name: str) -> Any:
    """
    📈 Service Performance Metrics
    
    Detailed performance and usage metrics for specific service.
    Critical for capacity planning and optimization.
    
    **Metrics Included:**
    - Request volume and patterns
    - Response time percentiles
    - Error rates and types
    - Resource consumption
    - Nigerian-specific usage patterns
    
    **Use Cases:**
    - Performance optimization
    - Capacity planning
    - SLA monitoring
    - Cost analysis
    """
    return health_service.get_service_metrics(service_name)


## (system_login declared above catch-all routes)


@router.get("/examples/nin")
async def nin_examples():
    """
    📋 NIN Verification Examples
    
    Sample requests and responses for Nigerian Identity Number verification.
    Essential reference for DPI integration.
    
    **Includes:**
    - Test NIN numbers for development
    - Request/response format examples
    - Expected data structure
    - Integration patterns
    
    **Nigerian Context:** Real NIN format and validation examples
    """
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
    """
    📱 Nigerian SMS Examples
    
    Sample SMS requests for Nigerian mobile networks.
    Includes OTP and bulk messaging patterns.
    
    **Features:**
    - Nigerian phone number formats
    - OTP message templates
    - Bulk SMS examples
    - Network-specific optimizations
    
    **Supported Networks:** MTN, Airtel, Glo, 9mobile
    """
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


## end system_login helpers
