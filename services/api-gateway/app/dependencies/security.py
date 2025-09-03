from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

security = HTTPBearer()

async def get_bearer_token(request: Request, credentials: Optional[HTTPAuthorizationCredentials] = None) -> str:
    """Extract and validate Bearer token from request."""
    
    # Try to get token from HTTPBearer dependency first
    if credentials and credentials.scheme.lower() == "bearer":
        token = credentials.credentials
        # Store token in request state for proxy forwarding
        request.state.bearer_token = token
        return token
    
    # Fallback: check Authorization header directly
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ", 1)[1]
        request.state.bearer_token = token
        return token
    
    # No token found
    raise HTTPException(status_code=403, detail="Not authenticated")