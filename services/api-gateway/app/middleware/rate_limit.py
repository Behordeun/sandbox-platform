import time

import redis
from app.core.config import settings
from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware using Redis."""

    def __init__(self, app):
        super().__init__(app)
        self.redis_client = None
        self.enabled = settings.rate_limit_enabled

        if self.enabled:
            try:
                self.redis_client = redis.from_url(settings.redis_url)
                # Test connection
                self.redis_client.ping()
            except Exception as e:
                print(f"Warning: Could not connect to Redis for rate limiting: {e}")
                self.enabled = False

    async def dispatch(self, request: Request, call_next):
        """Process request through rate limiting middleware."""
        if not self.enabled:
            return await call_next(request)

        # Get client identifier
        client_id = self._get_client_id(request)

        # Check rate limit
        if not await self._check_rate_limit(client_id):
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {settings.rate_limit_requests} requests per {settings.rate_limit_window} seconds",
                },
                headers={
                    "Retry-After": str(settings.rate_limit_window),
                    "X-RateLimit-Limit": str(settings.rate_limit_requests),
                    "X-RateLimit-Window": str(settings.rate_limit_window),
                },
            )

        response = await call_next(request)

        # Add rate limit headers to response
        remaining = await self._get_remaining_requests(client_id)
        response.headers["X-RateLimit-Limit"] = str(settings.rate_limit_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Window"] = str(settings.rate_limit_window)

        return response

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier for rate limiting."""
        # Try to get user ID from token
        if hasattr(request.state, "user_id") and request.state.user_id:
            return f"user:{request.state.user_id}"

        # Try to get API key
        if hasattr(request.state, "api_key") and request.state.api_key:
            return f"api_key:{request.state.api_key}"

        # Fall back to IP address
        client_ip = get_remote_address(request)
        return f"ip:{client_ip}"

    async def _check_rate_limit(self, client_id: str) -> bool:
        """Check if client has exceeded rate limit."""
        if not self.redis_client:
            return True

        try:
            current_time = int(time.time())
            window_start = current_time - settings.rate_limit_window

            # Use Redis sorted set for sliding window
            key = f"rate_limit:{client_id}"

            # Remove old entries
            self.redis_client.zremrangebyscore(key, 0, window_start)

            # Count current requests
            current_requests = self.redis_client.zcard(key)

            if current_requests >= settings.rate_limit_requests:
                return False

            # Add current request
            self.redis_client.zadd(key, {str(current_time): current_time})

            # Set expiration
            self.redis_client.expire(key, settings.rate_limit_window)

            return True

        except Exception as e:
            print(f"Rate limiting error: {e}")
            # Allow request if Redis is down
            return True

    async def _get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client."""
        if not self.redis_client:
            return settings.rate_limit_requests

        try:
            current_time = int(time.time())
            window_start = current_time - settings.rate_limit_window

            key = f"rate_limit:{client_id}"

            # Remove old entries
            self.redis_client.zremrangebyscore(key, 0, window_start)

            # Count current requests
            current_requests = self.redis_client.zcard(key)

            return max(0, settings.rate_limit_requests - current_requests)

        except Exception as e:
            print(f"Rate limiting error: {e}")
            return settings.rate_limit_requests
