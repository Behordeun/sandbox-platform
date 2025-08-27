from app.api.v1.router import api_router
from app.core.yaml_config import settings
from fastapi import FastAPI

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "nin-service"}
