from app.api.v1 import (
    ai_endpoints,
    auth_endpoints,
    bvn_endpoints,
    examples_endpoints,
    health_endpoints,
    nin_endpoints,
    sms_endpoints,
)
from fastapi import APIRouter

api_router = APIRouter()

# Include all service endpoints with automatic token forwarding
api_router.include_router(auth_endpoints.router, prefix="/auth", tags=["auth"])
api_router.include_router(nin_endpoints.router, prefix="/nin", tags=["nin"])
api_router.include_router(bvn_endpoints.router, prefix="/bvn", tags=["bvn"])
api_router.include_router(sms_endpoints.router, prefix="/sms", tags=["sms"])
api_router.include_router(ai_endpoints.router, prefix="/ai", tags=["ai"])
api_router.include_router(health_endpoints.router, tags=["health"])
api_router.include_router(
    examples_endpoints.router, prefix="/examples", tags=["examples"]
)
