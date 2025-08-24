from fastapi import APIRouter

api_router = APIRouter()

@api_router.get("/check")
async def health_check():
    return {"message": "Health check endpoint"}

@api_router.get("/services")
async def get_services_health():
    return {"message": "All services health status"}