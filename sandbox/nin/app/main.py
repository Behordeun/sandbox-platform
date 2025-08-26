from app.api.v1.router import api_router
from fastapi import FastAPI

app = FastAPI(title="NIN Service", version="1.0.0")

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "nin-service"}
