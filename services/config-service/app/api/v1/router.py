from app.api.v1 import config
from fastapi import APIRouter

api_router = APIRouter()

# Include config routes
api_router.include_router(config.router, prefix="/configs", tags=["configurations"])
