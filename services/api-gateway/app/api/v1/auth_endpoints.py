from app.services.proxy import proxy_service
from app.schemas.auth import UserLogin, UserCreate, UserUpdate, PasswordReset, OAuth2TokenRequest, OAuth2ClientCreate
from fastapi import APIRouter, Request, Body, Depends
from fastapi.security import HTTPBearer
from typing import Any

security = HTTPBearer()
router = APIRouter()

@router.post("/login", tags=["auth"])
async def login(request: Request, credentials: UserLogin = Body(...)) -> Any:
    """🔐 OAuth2 Compatible Login"""
    return await proxy_service.proxy_request(request, "auth", "/api/v1/auth/login")

@router.post("/login/json", tags=["auth"])
async def login_json(request: Request, credentials: UserLogin = Body(...)) -> Any:
    """🚀 JSON Login for Nigerian Startups"""
    return await proxy_service.proxy_request(request, "auth", "/api/v1/auth/login/json")

@router.get("/me", tags=["auth"], dependencies=[Depends(security)])
async def get_current_user_profile(request: Request) -> Any:
    """👤 Get Current User Profile"""
    return await proxy_service.proxy_request(request, "auth", "/api/v1/auth/me")

@router.post("/logout", tags=["auth"], dependencies=[Depends(security)])
async def logout(request: Request) -> Any:
    """🚪 User Logout"""
    return await proxy_service.proxy_request(request, "auth", "/api/v1/auth/logout")

@router.post("/token", tags=["auth"])
async def oauth_token(request: Request, token_data: OAuth2TokenRequest = Body(...)) -> Any:
    """🔑 OAuth2 Token Endpoint"""
    return await proxy_service.proxy_request(request, "auth", "/api/v1/oauth2/token")

# Admin endpoints
@router.post("/admin/users", tags=["auth", "admin"], dependencies=[Depends(security)])
async def create_user(request: Request, user_data: UserCreate = Body(...)) -> Any:
    """👥 Create User Account (Admin Only)"""
    return await proxy_service.proxy_request(request, "auth", "/api/v1/admin/users")

@router.get("/admin/users", tags=["auth", "admin"], dependencies=[Depends(security)])
async def list_users(request: Request) -> Any:
    """📋 List All Users (Admin Only)"""
    return await proxy_service.proxy_request(request, "auth", "/api/v1/admin/users")

@router.get("/admin/users/{user_id}", tags=["auth", "admin"], dependencies=[Depends(security)])
async def get_user(request: Request, user_id: int) -> Any:
    """👤 Get User by ID (Admin Only)"""
    return await proxy_service.proxy_request(request, "auth", f"/api/v1/admin/users/{user_id}")

@router.put("/admin/users/{user_id}", tags=["auth", "admin"], dependencies=[Depends(security)])
async def update_user(request: Request, user_id: int, user_data: UserUpdate = Body(...)) -> Any:
    """✏️ Update User (Admin Only)"""
    return await proxy_service.proxy_request(request, "auth", f"/api/v1/admin/users/{user_id}")

@router.delete("/admin/users/{user_id}", tags=["auth", "admin"], dependencies=[Depends(security)])
async def delete_user(request: Request, user_id: int) -> Any:
    """🗑️ Delete User (Admin Only)"""
    return await proxy_service.proxy_request(request, "auth", f"/api/v1/admin/users/{user_id}")

@router.post("/admin/users/{user_id}/activate", tags=["auth", "admin"], dependencies=[Depends(security)])
async def activate_user(request: Request, user_id: int) -> Any:
    """✅ Activate User Account (Admin Only)"""
    return await proxy_service.proxy_request(request, "auth", f"/api/v1/admin/users/{user_id}/activate")

@router.post("/admin/users/{user_id}/deactivate", tags=["auth", "admin"], dependencies=[Depends(security)])
async def deactivate_user(request: Request, user_id: int) -> Any:
    """❌ Deactivate User Account (Admin Only)"""
    return await proxy_service.proxy_request(request, "auth", f"/api/v1/admin/users/{user_id}/deactivate")

@router.post("/admin/users/{user_id}/reset-password", tags=["auth", "admin"], dependencies=[Depends(security)])
async def reset_user_password(request: Request, user_id: int, password_data: PasswordReset = Body(...)) -> Any:
    """🔑 Reset User Password (Admin Only)"""
    return await proxy_service.proxy_request(request, "auth", f"/api/v1/admin/users/{user_id}/reset-password")

# OAuth2 Client Management
@router.post("/oauth2/clients", tags=["auth", "oauth2"], dependencies=[Depends(security)])
async def create_oauth_client(request: Request, client_data: OAuth2ClientCreate = Body(...)) -> Any:
    """🔗 Create OAuth2 Client"""
    return await proxy_service.proxy_request(request, "auth", "/api/v1/oauth2/clients")

@router.get("/oauth2/clients/{client_id}", tags=["auth", "oauth2"], dependencies=[Depends(security)])
async def get_oauth_client(request: Request, client_id: str) -> Any:
    """🔍 Get OAuth2 Client"""
    return await proxy_service.proxy_request(request, "auth", f"/api/v1/oauth2/clients/{client_id}")

@router.get("/oauth2/authorize", tags=["auth", "oauth2"], dependencies=[Depends(security)])
async def oauth_authorize(request: Request) -> Any:
    """🔐 OAuth2 Authorization Endpoint"""
    return await proxy_service.proxy_request(request, "auth", "/api/v1/oauth2/authorize")
