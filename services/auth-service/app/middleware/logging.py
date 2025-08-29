import json
import logging
import time
import asyncio
from typing import Optional

from fastapi import Request
from app.core.security import verify_token
from sqlalchemy import text
from app.core.database import engine
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

        # Extract user info if available (state, forwarded header, or token)
        # First attempt before processing the request
        user_id = getattr(request.state, "user_id", None)
        if not user_id:
            user_id = request.headers.get("X-User-Id")
        if not user_id:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ", 1)[1]
                payload = verify_token(token, token_type="access")
                if payload and payload.get("sub"):
                    user_id = payload.get("sub")

        response = await call_next(request)

        # Resolve user_id again after endpoint runs (e.g., login sets request.state)
        final_user_id = (
            user_id
            or getattr(request.state, "user_id", None)
            or request.headers.get("X-User-Id")
        )

        # Log the activity
        self._log_user_activity(
            request, response, final_user_id, start_time, client_ip, user_agent
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
        request_id = getattr(request.state, "request_id", None)
        log_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()),
            "user_id": user_id,
            "request_id": request_id,
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

        # Persist audit to DB asynchronously (best-effort), skip /health
        if not str(request.url.path).endswith("/health"):
            try:
                asyncio.create_task(self._write_audit(log_data))
            except Exception:
                pass

    async def _write_audit(self, log: dict):
        if engine is None:
            return
        def _insert():
            try:
                with engine.begin() as conn:
                    conn.execute(
                        text(
                            """
                            INSERT INTO auth_audit_logs (
                                request_id, user_id, activity_type, success,
                                method, path, status_code, client_ip, user_agent
                            ) VALUES (
                                :request_id, :user_id, :activity_type, :success,
                                :method, :path, :status_code, :client_ip, :user_agent
                            )
                            """
                        ),
                        {
                            "request_id": str(log.get("request_id") or ""),
                            "user_id": int(log.get("user_id")) if str(log.get("user_id") or "").isdigit() else None,
                            "activity_type": str(log.get("activity_type") or ""),
                            "success": bool(log.get("success")),
                            "method": str(log.get("method") or ""),
                            "path": str(log.get("path") or ""),
                            "status_code": int(log.get("status_code") or 0),
                            "client_ip": str(log.get("client_ip") or ""),
                            "user_agent": str(log.get("user_agent") or ""),
                        },
                    )
            except Exception:
                pass
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _insert)

    def _get_activity_type(self, method: str, path: str) -> str:
        """Determine the type of user activity based on the request."""
        post_paths = {
            "/api/v1/auth/register": "user_registration",
            "/api/v1/auth/logout": "user_logout",
            "/api/v1/auth/password-reset/request": "password_reset_request",
            "/api/v1/auth/password-reset/verify": "password_reset_verify",
        }
        get_paths = {
            "/api/v1/auth/userinfo": "profile_access",
            "/api/v1/auth/me": "profile_access",
        }
        login_paths = {"/api/v1/auth/login", "/api/v1/auth/login/json"}

        if method == "POST":
            if path in post_paths:
                return post_paths[path]
            if path in login_paths:
                return "user_login"
        elif method == "GET" and path in get_paths:
            return get_paths[path]

        if path.startswith("/api/v1/oauth2/"):
            return "oauth2_flow"
        if "nin" in path or "bvn" in path:
            return "identity_verification"
        if path == "/health":
            return "health_check"
        return "api_access"

    def _get_verification_type(self, path: str) -> str:
        """Get the type of identity verification."""
        if "nin" in path:
            return "nin_verification"
        elif "bvn" in path:
            return "bvn_verification"
        else:
            return "unknown_verification"
