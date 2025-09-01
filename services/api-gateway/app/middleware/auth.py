import asyncio
import logging
import re
import time
from typing import List, Optional

import httpx
from app.core.config import settings
from app.core.security import validate_api_key, verify_token
from app.db import insert_gateway_access_log
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Configure structured logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("api_gateway.access")


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for API Gateway."""

    def __init__(self, app, excluded_paths: Optional[List[str]] = None):
        super().__init__(app)
        WELL_KNOWN_PATH = "/.well-known/"
        # Minimal exclusions - let backend services handle their own auth requirements
        self.excluded_paths = excluded_paths or [
            "/",
            "/health",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/api/v1/openapi.json",
            "/api/v1/services/health",
            "/api/v1/services/status",
            "/api/v1/examples/",
            WELL_KNOWN_PATH,
        ]

    async def dispatch(self, request: Request, call_next):
        """Process request through authentication middleware."""
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("User-Agent", "unknown")

        # Skip authentication for excluded paths
        if self._is_excluded_path(request.url.path):
            response = await call_next(request)
            self._log_access(
                request, response, "", "public", start_time, client_ip, user_agent
            )
            return response

        # Extract authentication credentials
        auth_header = request.headers.get("Authorization")
        api_key = request.headers.get("X-API-Key")
        session_id = request.cookies.get("session_id")

        user_id = None
        auth_method = None

        # Pass through to backend services - let them handle auth requirements
        # Only validate if credentials are provided
        if auth_header:
            user_id, auth_method, error_response = self._authenticate_jwt(request, auth_header, start_time, client_ip, user_agent)
            if error_response:
                return error_response
        elif api_key:
            user_id, auth_method, error_response = self._authenticate_api_key(request, api_key, start_time, client_ip, user_agent)
            if error_response:
                return error_response
        elif session_id:
            user_id, auth_method, error_response = await self._authenticate_session(request, session_id, start_time, client_ip, user_agent)
            if error_response:
                return error_response
        else:
            # No credentials provided - pass through to backend
            auth_method = "passthrough"



        response = await call_next(request)
        self._log_access(
            request,
            response,
            user_id if user_id is not None else "",
            auth_method if auth_method is not None else "",
            start_time,
            client_ip,
            user_agent,
        )
        return response

    def _authenticate_jwt(self, request, auth_header, start_time, client_ip, user_agent):
        if not auth_header.startswith("Bearer "):
            response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Invalid authorization header format"},
            )
            self._log_access(
                request,
                response,
                "",
                "invalid_token_format",
                start_time,
                client_ip,
                user_agent,
            )
            return None, None, response

        token = auth_header.split(" ")[1]
        payload = verify_token(token)

        if not payload:
            response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Invalid or expired token"},
            )
            self._log_access(
                request,
                response,
                "",
                "invalid_token",
                start_time,
                client_ip,
                user_agent,
            )
            return None, None, response

        user_id = payload.get("sub")
        request.state.user_id = user_id
        request.state.token_payload = payload
        return user_id, "jwt_token", None

    def _authenticate_api_key(self, request, api_key, start_time, client_ip, user_agent):
        if not validate_api_key(api_key):
            response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Invalid API key"},
            )
            self._log_access(
                request,
                response,
                "",
                "invalid_api_key",
                start_time,
                client_ip,
                user_agent,
            )
            return None, None, response

        request.state.api_key = api_key
        return "api_key_user", "api_key", None

    async def _authenticate_session(self, request, session_id, start_time, client_ip, user_agent):
        session_data = await self._validate_session(session_id)
        if not session_data:
            response = JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"error": "Invalid or expired session"},
            )
            self._log_access(
                request,
                response,
                "",
                "invalid_session",
                start_time,
                client_ip,
                user_agent,
            )
            return None, None, response

        user_id = session_data.get("user_id")
        request.state.user_id = user_id
        request.state.session_data = session_data
        return user_id, "session_id", None

    def _log_access(
        self,
        request: Request,
        response,
        user_id: str,
        auth_method: str,
        start_time: float,
        client_ip: str,
        user_agent: str,
    ):
        """Log detailed access information for monitoring and analytics."""
        duration = round((time.time() - start_time) * 1000, 2)  # milliseconds

        # Determine service being accessed
        service_name = self._extract_service_name(request.url.path)

        # Create structured log entry
        request_id = getattr(request.state, "request_id", None)
        log_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "user_id": user_id,
            "auth_method": auth_method,
            "method": request.method,
            "path": request.url.path,
            "service": service_name,
            "status_code": response.status_code,
            "duration_ms": duration,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "request_id": request_id,
            "query_params": str(request.query_params) if request.query_params else None,
        }

        # Augment with sizes
        try:
            req_size = int(request.headers.get("content-length", "0") or 0)
        except Exception:
            req_size = 0
        try:
            res_size = int(response.headers.get("content-length", "0") or 0)
        except Exception:
            res_size = 0
        log_data["req_size"] = req_size
        log_data["res_size"] = res_size

        # Log with appropriate level based on status code
        if response.status_code >= 400:
            logger.warning(f"ACCESS_DENIED: {log_data}")
        else:
            logger.info(f"ACCESS_GRANTED: {log_data}")

        # Persist to DB asynchronously (best-effort), but skip health endpoints
        try:
            if not str(request.url.path).endswith("/health"):
                _task = asyncio.create_task(insert_gateway_access_log(log_data))
        except Exception:
            pass

    def _extract_service_name(self, path: str) -> str:
        """Extract service name from request path."""
        if path.startswith("/api/v1/auth"):
            return "auth-service"
        elif path.startswith("/api/v1/nin"):
            return "nin-service"
        elif path.startswith("/api/v1/bvn"):
            return "bvn-service"
        elif path.startswith("/api/v1/sms"):
            return "sms-service"
        elif path.startswith("/api/v1/ai") or path.startswith("/api/v1/llm"):
            return "ai-service"
        elif path.startswith("/api/v1/ivr"):
            return "ivr-service"
        elif path.startswith("/api/v1/services"):
            return "gateway-health"
        else:
            return "api-gateway"

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

    async def _validate_session(self, session_id: str) -> Optional[dict]:
        """Validate session ID with auth service."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{settings.auth_service_url}/api/v1/auth/me",
                    cookies={"session_id": session_id}
                )
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception:
            return None
