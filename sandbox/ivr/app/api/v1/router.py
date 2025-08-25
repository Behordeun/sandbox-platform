from fastapi import APIRouter

api_router = APIRouter()

@api_router.post("/call")
async def initiate_call():
    return {"message": "IVR call initiated"}

@api_router.get("/menu")
async def get_menu():
    return {"message": "IVR menu configuration"}