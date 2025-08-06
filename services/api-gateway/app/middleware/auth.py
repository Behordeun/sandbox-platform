from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import List
import re

from app.core.security import verify_token, validate_api_key


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for API Gateway."""
    
    def __init__(self, app, excluded_paths: List[str] = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or [
            "/health",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/auth/register",
            "/api/v1/auth/login",
            "/.well-known/"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """Process request through authentication middleware."""
        # Skip authentication for excluded paths
        if self._is_excluded_path(request.url.path):
            return await call_next(request)
        
        # Extract authentication credentials
        auth_header = request.headers.get("Authorization")
        api_key = request.headers.get("X-API-Key")
        
        # Check for authentication credentials
        if not auth_header and not api_key:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Authentication required"}
            )
        
        # Validate JWT token
        if auth_header:
            if not auth_header.startswith("Bearer "):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"error": "Invalid authorization header format"}
                )
            
            token = auth_header.split(" ")[1]
            payload = verify_token(token)
            
            if not payload:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"error": "Invalid or expired token"}
                )
            
            # Add user info to request state
            request.state.user_id = payload.get("sub")
            request.state.token_payload = payload
        
        # Validate API key
        elif api_key:
            if not validate_api_key(api_key):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"error": "Invalid API key"}
                )
            
            # Add API key info to request state
            request.state.api_key = api_key
        
        return await call_next(request)
    
    def _is_excluded_path(self, path: str) -> bool:
        """Check if path is excluded from authentication."""
        for excluded_path in self.excluded_paths:
            if excluded_path.endswith("/"):
                if path.startswith(excluded_path):
                    return True
            else:
                if path == excluded_path or re.match(f"^{excluded_path}.*", path):
                    return True
        return False

