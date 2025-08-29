import asyncio
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from ..db import insert_access_log


class AccessLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration_ms = int((time.time() - start) * 1000)
        # Resolve user id from state or forwarded header
        forwarded_user = request.headers.get("X-User-Id")
        resolved_user_id = getattr(request.state, "user_id", None) or forwarded_user
        log = {
            "request_id": getattr(request.state, "request_id", None),
            "user_id": resolved_user_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent", "unknown"),
        }
        try:
            log["req_size"] = int(request.headers.get("content-length", "0") or 0)
        except Exception:
            log["req_size"] = 0
        try:
            log["res_size"] = int(response.headers.get("content-length", "0") or 0)
        except Exception:
            log["res_size"] = 0
        # Skip DB writes for health endpoints
        if not str(request.url.path).endswith("/health"):
            try:
                asyncio.create_task(insert_access_log(log))
            except Exception:
                pass
        return response
