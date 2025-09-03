from typing import Callable

from app.core.security import verify_token
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class TokenForwardingMiddleware(BaseHTTPMiddleware):
    """Middleware to extract and validate bearer tokens for automatic forwarding."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract bearer token from Authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]

            # Verify token and extract user info
            payload = verify_token(token)
            if payload:
                user_id = payload.get("sub")
                if user_id:
                    # Store user context in request state for automatic forwarding
                    request.state.user_id = int(user_id)
                    request.state.token_payload = payload
                    request.state.bearer_token = token

        response = await call_next(request)
        return response
