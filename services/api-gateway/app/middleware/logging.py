import json
import logging
import time
from typing import Callable, Optional

from app.core.config import settings
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logger
logger = logging.getLogger("api_gateway")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logging middleware for API Gateway."""

    def __init__(self, app):
        super().__init__(app)
        self.request_logging_enabled = settings.request_logging_enabled
        self.response_logging_enabled = settings.response_logging_enabled

    async def dispatch(self, request: Request, call_next: Callable):
        """Process request through logging middleware."""
        start_time = time.time()

        # Log request
        if self.request_logging_enabled:
            await self._log_request(request)

        # Process request
        response = await call_next(request)

        # Calculate processing time
        process_time = time.time() - start_time

        # Log response
        if self.response_logging_enabled:
            await self._log_response(request, response, process_time)

        # Add processing time header
        response.headers["X-Process-Time"] = str(process_time)

        return response

    async def _log_request(self, request: Request):
        """Log incoming request."""
        # Get client info
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Get user info if available
        user_id = getattr(request.state, "user_id", None)
        api_key = getattr(request.state, "api_key", None)

        # Prepare log data
        log_data = {
            "event": "request",
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "client_ip": client_ip,
            "user_agent": user_agent,
            "user_id": user_id,
            "has_api_key": bool(api_key),
            "headers": dict(request.headers),
            "timestamp": time.time(),
        }

        # Remove sensitive headers
        sensitive_headers = ["authorization", "x-api-key", "cookie"]
        for header in sensitive_headers:
            if header in log_data["headers"]:
                log_data["headers"][header] = "[REDACTED]"

        logger.info(f"Request: {json.dumps(log_data)}")

    async def _log_response(self, request: Request, response, process_time: float):
        """Log outgoing response."""
        # Get client info
        client_ip = request.client.host if request.client else "unknown"
        user_id = getattr(request.state, "user_id", None)

        # Prepare log data
        log_data = {
            "event": "response",
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "status_code": response.status_code,
            "client_ip": client_ip,
            "user_id": user_id,
            "process_time": process_time,
            "response_headers": dict(response.headers),
            "timestamp": time.time(),
        }

        # Log level based on status code
        if response.status_code >= 500:
            logger.error(f"Response: {json.dumps(log_data)}")
        elif response.status_code >= 400:
            logger.warning(f"Response: {json.dumps(log_data)}")
        else:
            logger.info(f"Response: {json.dumps(log_data)}")


class StructuredLogger:
    """Structured logger for API Gateway."""

    def __init__(self, name: str = "api_gateway"):
        self.logger = logging.getLogger(name)

    def log_service_call(
        self,
        service_name: str,
        method: str,
        url: str,
        status_code: int,
        response_time: float,
        error: Optional[str] = None,
    ):
        """Log service call."""
        log_data = {
            "event": "service_call",
            "service": service_name,
            "method": method,
            "url": url,
            "status_code": status_code,
            "response_time": response_time,
            "timestamp": time.time(),
        }

        if error:
            log_data["error"] = error
            self.logger.error(f"Service call failed: {json.dumps(log_data)}")
        else:
            self.logger.info(f"Service call: {json.dumps(log_data)}")

    def log_circuit_breaker_event(
        self,
        service_name: str,
        event: str,
        state: str,
        failure_count: Optional[int] = None,
    ):
        """Log circuit breaker event."""
        log_data = {
            "event": "circuit_breaker",
            "service": service_name,
            "circuit_breaker_event": event,
            "state": state,
            "timestamp": time.time(),
        }

        if failure_count is not None:
            log_data["failure_count"] = failure_count

        self.logger.warning(f"Circuit breaker: {json.dumps(log_data)}")


# Global structured logger
structured_logger = StructuredLogger()
