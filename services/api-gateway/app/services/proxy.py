import time
from typing import Any, Dict, Optional

import httpx
from app.core.circuit_breaker import (
    CircuitBreakerOpenException,
    circuit_breaker_manager,
)
from app.core.config import ServiceConfig, settings
from app.middleware.logging import structured_logger
from app.middleware.metrics import metrics_collector
from fastapi import HTTPException, Request
from fastapi.responses import Response


class ProxyService:
    """Service for proxying requests to backend services."""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=settings.default_timeout)

    async def proxy_request(
        self, request: Request, service_name: str, path: Optional[str] = None
    ) -> Response:
        """Proxy request to backend service."""
        # Get service configuration
        service_config = settings.services.get(service_name)
        if not service_config:
            raise HTTPException(
                status_code=404, detail=f"Service '{service_name}' not found"
            )

        # Build target URL
        target_path = path or request.url.path
        if target_path.startswith(f"/api/v1/{service_name}"):
            # Remove service prefix from path
            target_path = target_path.replace(f"/api/v1/{service_name}", "", 1)
            if not target_path.startswith("/"):
                target_path = "/" + target_path

        target_url = f"{service_config.url}{target_path}"
        if request.url.query:
            target_url += f"?{request.url.query}"

        # Get circuit breaker
        circuit_breaker = circuit_breaker_manager.get_breaker(service_name)

        try:
            # Make request through circuit breaker
            response = await circuit_breaker.call(
                self._make_request, request, target_url, service_config
            )
            return response

        except CircuitBreakerOpenException:
            structured_logger.log_circuit_breaker_event(
                service_name, "request_blocked", "open"
            )
            raise HTTPException(
                status_code=503,
                detail=f"Service '{service_name}' is temporarily unavailable",
            )
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504, detail=f"Service '{service_name}' request timeout"
            )
        except httpx.ConnectError:
            raise HTTPException(
                status_code=503, detail=f"Service '{service_name}' is unavailable"
            )
        except Exception as e:
            structured_logger.logger.error(f"Proxy error for {service_name}: {e}")
            raise HTTPException(status_code=502, detail=f"Bad gateway: {str(e)}")

    async def _make_request(
        self, request: Request, target_url: str, service_config: ServiceConfig
    ) -> Response:
        """Make HTTP request to backend service."""
        start_time = time.time()

        # Prepare headers
        headers = dict(request.headers)

        # Remove hop-by-hop headers
        hop_by_hop_headers = [
            "connection",
            "keep-alive",
            "proxy-authenticate",
            "proxy-authorization",
            "te",
            "trailers",
            "transfer-encoding",
            "upgrade",
        ]
        for header in hop_by_hop_headers:
            headers.pop(header, None)

        # Add forwarded headers
        if request.client:
            headers["X-Forwarded-For"] = request.client.host
        headers["X-Forwarded-Proto"] = request.url.scheme
        headers["X-Forwarded-Host"] = request.headers.get("host", "")

        # Get request body
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()

        try:
            # Make request
            response = await self.client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                timeout=service_config.timeout,
            )

            # Record metrics
            duration = time.time() - start_time
            metrics_collector.record_service_request(
                service_config.name, request.method, response.status_code, duration
            )

            # Log service call
            structured_logger.log_service_call(
                service_config.name,
                request.method,
                target_url,
                response.status_code,
                duration,
            )

            # Create response
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type"),
            )

        except Exception as e:
            # Record error metrics
            duration = time.time() - start_time
            metrics_collector.record_service_request(
                service_config.name, request.method, 500, duration
            )

            # Log error
            structured_logger.log_service_call(
                service_config.name, request.method, target_url, 500, duration, str(e)
            )

            raise e

    async def health_check_service(self, service_name: str) -> Dict[str, Any]:
        """Check health of a backend service."""
        service_config = settings.services.get(service_name)
        if not service_config:
            return {
                "service": service_name,
                "status": "unknown",
                "error": "Service not configured",
            }

        health_url = f"{service_config.url}{service_config.health_path}"

        try:
            response = await self.client.get(health_url, timeout=10.0)

            if response.status_code == 200:
                return {
                    "service": service_name,
                    "status": "healthy",
                    "response_time": response.elapsed.total_seconds(),
                    "url": service_config.url,
                }
            else:
                return {
                    "service": service_name,
                    "status": "unhealthy",
                    "status_code": response.status_code,
                    "url": service_config.url,
                }

        except Exception as e:
            # Log exception with stack trace internally
            structured_logger.log_error(
                f"Error checking health for service '{service_name}' at {health_url}: {str(e)}",
                exc_info=True,
            )
            # Return only a generic error message to callers
            return {
                "service": service_name,
                "status": "unhealthy",
                "error": "An internal error occurred",
                "url": service_config.url,
            }

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()


# Global proxy service instance
proxy_service = ProxyService()
