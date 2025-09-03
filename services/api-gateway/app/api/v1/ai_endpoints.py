from app.services.proxy import proxy_service
from app.schemas.dpi import AIChatRequest, AIGenerateRequest, AIAnalyzeRequest, AITranslateRequest
from fastapi import APIRouter, Request, Body, Depends
from fastapi.security import HTTPBearer
from typing import Any

security = HTTPBearer()
router = APIRouter()

@router.post("/chat", tags=["ai"], dependencies=[Depends(security)])
async def chat_completion(request: Request, chat_data: AIChatRequest = Body(...)) -> Any:
    """🤖 Interactive Chat Completion"""
    return await proxy_service.proxy_request(request, "ai", "/api/v1/ai/chat")

@router.post("/generate", tags=["ai"], dependencies=[Depends(security)])
async def generate_content(request: Request, generation_data: AIGenerateRequest = Body(...)) -> Any:
    """📝 Generate Content"""
    return await proxy_service.proxy_request(request, "ai", "/api/v1/ai/generate")

@router.post("/analyze", tags=["ai"], dependencies=[Depends(security)])
async def analyze_text(request: Request, analysis_data: AIAnalyzeRequest = Body(...)) -> Any:
    """🔍 Analyze Text Content"""
    return await proxy_service.proxy_request(request, "ai", "/api/v1/ai/analyze")

@router.post("/translate", tags=["ai"], dependencies=[Depends(security)])
async def translate_text(request: Request, translation_data: AITranslateRequest = Body(...)) -> Any:
    """🌍 Nigerian Language Translation"""
    return await proxy_service.proxy_request(request, "ai", "/api/v1/ai/translate")

@router.get("/models", tags=["ai"], dependencies=[Depends(security)])
async def get_available_models(request: Request) -> Any:
    """🧠 Get Available AI Models"""
    return await proxy_service.proxy_request(request, "ai", "/api/v1/ai/models")

@router.get("/conversations/{conversation_id}", tags=["ai"], dependencies=[Depends(security)])
async def get_conversation(request: Request, conversation_id: str) -> Any:
    """💬 Get Conversation History"""
    return await proxy_service.proxy_request(request, "ai", f"/api/v1/ai/conversations/{conversation_id}")

@router.get("/usage", tags=["ai"], dependencies=[Depends(security)])
async def get_usage_statistics(request: Request) -> Any:
    """📊 Get Token Usage Statistics"""
    return await proxy_service.proxy_request(request, "ai", "/api/v1/ai/usage")
