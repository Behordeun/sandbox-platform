import json

import redis
from app.core.config import settings
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class CacheMiddleware(BaseHTTPMiddleware):
    """Simple caching middleware for API responses"""

    def __init__(self, app):
        super().__init__(app)
        self.redis_client = None
        self.enabled = settings.rate_limit_enabled  # Reuse Redis connection

        if self.enabled:
            try:
                self.redis_client = redis.from_url(settings.redis_url)
                self.redis_client.ping()
            except Exception:
                self.enabled = False

    async def dispatch(self, request: Request, call_next):
        """Cache GET requests for cacheable endpoints"""
        if not self.enabled or request.method != "GET":
            return await call_next(request)

        # Only cache specific endpoints
        cacheable_paths = ["/api/v1/dpi/health", "/api/v1/services/health"]
        if not any(request.url.path.startswith(path) for path in cacheable_paths):
            return await call_next(request)

        # Generate cache key
        cache_key = f"cache:{request.url.path}:{request.url.query}"

        try:
            # Check cache
            cached = self.redis_client.get(cache_key)
            if cached:
                data = json.loads(cached)
                from fastapi.responses import JSONResponse

                return JSONResponse(content=data)
        except Exception:
            pass

        # Process request
        response = await call_next(request)

        # Cache successful responses
        if response.status_code == 200:
            try:
                # Cache for 30 seconds
                self.redis_client.setex(cache_key, 30, response.body)
            except Exception:
                pass

        return response
