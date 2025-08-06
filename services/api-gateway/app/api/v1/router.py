from app.api.v1 import gateway
from fastapi import APIRouter

api_router = APIRouter()

# Include gateway routes
api_router.include_router(gateway.router, tags=["gateway"])
