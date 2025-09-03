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
        self,
        request: Request,
        service_name: str,
        path: Optional[str] = None,
        json_payload: Optional[Dict[str, Any]] = None,
        **kwargs
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
        # Normalize leading slash
        if not target_path.startswith("/"):
            target_path = "/" + target_path

        # If the path isn't already versioned, add '/api/v1/<service>/' prefix
        if not target_path.startswith("/api/v1/"):
            # Map service name to its path segment (llm mapped upstream to 'ai')
            service_segment = service_name
            target_path = f"/api/v1/{service_segment}{target_path}"

        target_url = f"{service_config.url}{target_path}"
        if request.url.query:
            target_url += f"?{request.url.query}"

        # Get circuit breaker
        circuit_breaker = circuit_breaker_manager.get_breaker(service_name)

        try:
            # Make request through circuit breaker
            response = await circuit_breaker.call(
                self._make_request, request, target_url, service_config, json_payload
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
        self,
        request: Request,
        target_url: str,
        service_config: ServiceConfig,
        json_payload: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """Make HTTP request to backend service."""
        start_time = time.time()

        headers = self._prepare_proxy_headers(request)

        # Handle request body and parameters
        body = None
        params = dict(request.query_params)
        
        if request.method in ["POST", "PUT", "PATCH"]:
            if json_payload is not None:
                import json
                body = json.dumps(json_payload).encode("utf-8")
                headers["content-type"] = "application/json"
            else:
                content_type = request.headers.get("content-type", "")
                if "application/json" in content_type:
                    body = await request.body()
                elif "application/x-www-form-urlencoded" in content_type:
                    form_data = await request.form()
                    body = "&".join([f"{k}={v}" for k, v in form_data.items()]).encode("utf-8")
                else:
                    body = await request.body()

        try:
            response = await self.client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=params,
                timeout=service_config.timeout,
            )

            duration = time.time() - start_time
            metrics_collector.record_service_request(
                service_config.name, request.method, response.status_code, duration
            )

            structured_logger.log_service_call(
                service_config.name,
                request.method,
                target_url,
                response.status_code,
                duration,
            )

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.headers.get("content-type"),
            )

        except Exception as e:
            duration = time.time() - start_time
            metrics_collector.record_service_request(
                service_config.name, request.method, 500, duration
            )

            structured_logger.log_service_call(
                service_config.name, request.method, target_url, 500, duration, str(e)
            )

            raise e

    def _prepare_proxy_headers(self, request: Request) -> Dict[str, str]:
        """Prepare headers for proxying, including token forwarding."""
        headers = dict(request.headers)
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
        headers.pop("content-length", None)

        if request.client:
            headers["X-Forwarded-For"] = request.client.host
        headers["X-Forwarded-Proto"] = request.url.scheme
        headers["X-Forwarded-Host"] = request.headers.get("host", "")
        request_id = getattr(request.state, "request_id", None)
        if request_id:
            headers["X-Request-ID"] = request_id
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            headers["X-User-Id"] = str(user_id)

        # Get token from request state (set by security dependency) or headers
        token = getattr(request.state, "bearer_token", None)
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ", 1)[1]
        if token:
            headers["Authorization"] = f"Bearer {token}"

        return headers

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

        except (httpx.ConnectError, httpx.TimeoutException) as e:
            # Log connection errors at debug level to reduce noise during startup
            structured_logger.logger.debug(
                f"Health check failed for service '{service_name}' at {health_url}: {str(e)}"
            )
            return {
                "service": service_name,
                "status": "unhealthy",
                "error": "Service unavailable",
                "url": service_config.url,
            }
        except Exception as e:
            # Log other exceptions with stack trace
            structured_logger.log_error(
                f"Error checking health for service '{service_name}' at {health_url}: {str(e)}",
                exc_info=True,
            )
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
