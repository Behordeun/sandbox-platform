import json
import logging
import time
from typing import Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Configure structured logging for user activities
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("auth_service.user_activity")


class UserActivityLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log detailed user activities in Auth Service."""

    async def dispatch(self, request: Request, call_next):
        """Log user activities with rich context."""
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("User-Agent", "unknown")

        # Extract user info if available
        user_id = getattr(request.state, "user_id", None)

        response = await call_next(request)

        # Log the activity
        self._log_user_activity(
            request, response, user_id, start_time, client_ip, user_agent
        )

        return response

    def _log_user_activity(
        self,
        request: Request,
        response,
        user_id: Optional[str],
        start_time: float,
        client_ip: str,
        user_agent: str,
    ):
        """Log detailed user activity information."""
        duration = round((time.time() - start_time) * 1000, 2)  # milliseconds

        # Determine activity type
        activity_type = self._get_activity_type(request.method, request.url.path)

        # Create structured log entry
        log_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "user_id": user_id,
            "activity_type": activity_type,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration,
            "client_ip": client_ip,
            "user_agent": user_agent,
            "success": response.status_code < 400,
        }

        # Add specific context for important activities
        if activity_type in [
            "user_registration",
            "user_login",
            "password_reset_request",
        ]:
            log_data["security_event"] = True

        if activity_type == "identity_verification":
            log_data["verification_type"] = self._get_verification_type(
                request.url.path
            )

        # Log with appropriate level
        if response.status_code >= 400:
            if activity_type in ["user_login", "token_validation"]:
                logger.warning(f"SECURITY_EVENT: {json.dumps(log_data)}")
            else:
                logger.warning(f"USER_ACTIVITY_FAILED: {json.dumps(log_data)}")
        else:
            if activity_type in [
                "user_registration",
                "user_login",
                "password_reset_request",
            ]:
                logger.info(f"SECURITY_EVENT: {json.dumps(log_data)}")
            else:
                logger.info(f"USER_ACTIVITY: {json.dumps(log_data)}")

    def _get_activity_type(self, method: str, path: str) -> str:
        """Determine the type of user activity based on the request."""
        if path == "/api/v1/auth/register" and method == "POST":
            return "user_registration"
        elif (
            path in ["/api/v1/auth/login", "/api/v1/auth/login/json"]
            and method == "POST"
        ):
            return "user_login"
        elif path == "/api/v1/auth/logout" and method == "POST":
            return "user_logout"
        elif path in ["/api/v1/auth/userinfo", "/api/v1/auth/me"] and method == "GET":
            return "profile_access"
        elif path == "/api/v1/auth/password-reset/request" and method == "POST":
            return "password_reset_request"
        elif path == "/api/v1/auth/password-reset/verify" and method == "POST":
            return "password_reset_verify"
        elif path.startswith("/api/v1/oauth2/"):
            return "oauth2_flow"
        elif "nin" in path or "bvn" in path:
            return "identity_verification"
        elif path == "/health":
            return "health_check"
        else:
            return "api_access"

    def _get_verification_type(self, path: str) -> str:
        """Get the type of identity verification."""
        if "nin" in path:
            return "nin_verification"
        elif "bvn" in path:
            return "bvn_verification"
        else:
            return "unknown_verification"
