from fastapi import APIRouter

api_router = APIRouter()


@api_router.post("/send")
async def send_sms():
    return {"message": "Two-way SMS send endpoint"}


@api_router.post("/receive")
async def receive_sms():
    return {"message": "Two-way SMS receive endpoint"}
