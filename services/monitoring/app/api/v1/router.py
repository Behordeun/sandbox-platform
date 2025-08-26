from fastapi import APIRouter

api_router = APIRouter()


@api_router.get("/metrics")
async def get_metrics():
    return {"message": "System metrics endpoint"}


@api_router.get("/alerts")
async def get_alerts():
    return {"message": "System alerts endpoint"}
