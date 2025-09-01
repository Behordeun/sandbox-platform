import httpx
from app.core.config import settings
from app.core.security import verify_token
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing import Optional

# OAuth2 scheme for token authentication
oauth2_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(oauth2_scheme),
) -> dict:
    """Get current authenticated user from JWT token or session."""
    
    # Try bearer token first
    if credentials:
        token = credentials.credentials
        payload = verify_token(token, token_type="access")
        if payload:
            user_id = payload.get("sub")
            if user_id:
                request.state.user_id = int(user_id)
                return {"user_id": int(user_id), "auth_method": "bearer_token"}
    
    # Try session cookie
    session_id = request.cookies.get("session_id")
    if session_id:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{settings.auth_service_url}/api/v1/auth/me",
                    cookies={"session_id": session_id}
                )
                if response.status_code == 200:
                    user_data = response.json()
                    user_id = user_data.get("id")
                    if user_id:
                        request.state.user_id = user_id
                        return {"user_id": user_id, "auth_method": "session"}
        except Exception:
            pass
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_optional_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(oauth2_scheme),
) -> Optional[dict]:
    """Get current user if authenticated, otherwise return None."""
    try:
        return await get_current_user(request, credentials)
    except HTTPException:
        return None