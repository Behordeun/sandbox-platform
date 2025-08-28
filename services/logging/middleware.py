"""
FastAPI Middleware for Automatic Logging Integration
Automatically logs all API requests, responses, and user activities
"""

import time
from typing import Callable, Optional

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .rotational_logger import get_logger, log_startup_access


class DPILoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically log all API interactions"""

    def __init__(self, app, service_name: str, log_dir: str = "logs"):
        super().__init__(app)
        self.service_name = service_name
        self.logger = get_logger(service_name, log_dir)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Start timing
        start_time = time.time()

        # Extract request information
        method = request.method
        path = str(request.url.path)
        client_ip = self._get_client_ip(request)
        user_agent = request.headers.get("user-agent", "")

        # Extract user information if available
        user_id = None
        startup_name = None

        # Try to get user from JWT token or session
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            user_info = self._extract_user_from_token(auth_header)
            user_id = user_info.get("user_id")
            startup_name = user_info.get("startup_name")

        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
            error_details = None
        except Exception as e:
            status_code = 500
            error_details = {"error": str(e), "type": type(e).__name__}
            response = JSONResponse(
                status_code=500, content={"error": "Internal server error"}
            )

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Log API access
        self.logger.log_api_access(
            method=method,
            path=path,
            status_code=status_code,
            duration_ms=duration_ms,
            user_id=user_id,
            client_ip=client_ip,
            user_agent=user_agent,
            startup_name=startup_name,
            error_details=error_details,
        )

        # Log startup-specific access if applicable
        if startup_name and user_id:
            log_startup_access(
                service=self.service_name,
                startup_name=startup_name,
                user_id=user_id,
                api_endpoint=path,
                method=method,
                status_code=status_code,
                duration_ms=duration_ms,
                client_ip=client_ip,
            )

        # Log security events for suspicious activities
        self._check_security_events(request, response, user_id, client_ip)

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address considering proxies"""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        return request.client.host if request.client else "unknown"

    def _extract_user_from_token(self, auth_header: str) -> dict:
        """Extract user information from JWT token"""
        try:
            # This is a simplified version - in production, properly decode JWT
            auth_header.replace("Bearer ", "")
            # For now, return empty dict - implement JWT decoding as needed
            return {}
        except Exception:
            return {}

    def _check_security_events(
        self,
        request: Request,
        response: Response,
        user_id: Optional[str],
        client_ip: str,
    ):
        """Check for security events and log them"""

        # Failed authentication attempts
        if response.status_code == 401:
            self.logger.log_security_event(
                event_type="AUTHENTICATION_FAILURE",
                severity="MEDIUM",
                details={
                    "path": str(request.url.path),
                    "client_ip": client_ip,
                    "user_id": user_id,
                    "user_agent": request.headers.get("user-agent", ""),
                },
            )

        # Multiple failed attempts from same IP (simplified check)
        elif response.status_code == 429:  # Rate limited
            self.logger.log_security_event(
                event_type="RATE_LIMIT_EXCEEDED",
                severity="HIGH",
                details={
                    "client_ip": client_ip,
                    "path": str(request.url.path),
                    "user_id": user_id,
                },
            )

        # Suspicious paths
        suspicious_paths = ["/admin", "/.env", "/config", "/debug"]
        if any(
            suspicious in str(request.url.path).lower()
            for suspicious in suspicious_paths
        ):
            if not user_id:  # Unauthenticated access to sensitive paths
                self.logger.log_security_event(
                    event_type="SUSPICIOUS_PATH_ACCESS",
                    severity="HIGH",
                    details={
                        "path": str(request.url.path),
                        "client_ip": client_ip,
                        "authenticated": bool(user_id),
                    },
                )
