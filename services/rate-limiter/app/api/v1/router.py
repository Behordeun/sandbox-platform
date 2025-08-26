from fastapi import APIRouter

api_router = APIRouter()


@api_router.post("/limit")
async def check_rate_limit():
    return {"message": "Rate limit check endpoint"}


@api_router.get("/status")
async def get_rate_limit_status():
    return {"message": "Rate limit status"}
