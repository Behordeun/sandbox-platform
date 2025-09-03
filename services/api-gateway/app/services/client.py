import time
from typing import Any, Dict, Optional

import httpx
from app.core.circuit_breaker import CircuitBreakerOpenException, circuit_breaker_manager
from app.core.config import ServiceConfig, settings
from app.middleware.logging import structured_logger
from app.middleware.metrics import metrics_collector
from fastapi import HTTPException, Request

APPLICATION_JSON = "application/json"


class ServiceClient:
    """HTTP client for making requests to backend services with automatic token forwarding."""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=settings.default_timeout)

    async def make_request(
        self,
        request: Request,
        service_name: str,
        method: str,
        path: str,
        json_payload: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, Any]] = None,
        form_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make authenticated request to backend service."""
        service_config = settings.services.get(service_name)
        if not service_config:
            raise HTTPException(
                status_code=404, detail=f"Service '{service_name}' not found"
            )

        target_url = f"{service_config.url}{path}"
        circuit_breaker = circuit_breaker_manager.get_breaker(service_name)

        try:
            response = await circuit_breaker.call(
                self._execute_request,
                request,
                target_url,
                method,
                service_config,
                json_payload,
                query_params,
                form_data,
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
        except HTTPException:
            raise
        except Exception as e:
            structured_logger.logger.error(f"Service request error for {service_name}: {e}")
            raise HTTPException(status_code=502, detail=f"Bad gateway: {str(e)}")

    async def _execute_request(
        self,
        request: Request,
        target_url: str,
        method: str,
        service_config: ServiceConfig,
        json_payload: Optional[Dict[str, Any]] = None,
        query_params: Optional[Dict[str, Any]] = None,
        form_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Execute HTTP request to backend service."""
        start_time = time.time()
        headers = self._prepare_headers(request)

        try:
            request_kwargs = {
                "method": method,
                "url": target_url,
                "headers": headers,
                "params": query_params,
                "timeout": service_config.timeout,
            }

            if form_data:
                request_kwargs["data"] = form_data
            elif json_payload:
                request_kwargs["json"] = json_payload

            response = await self.client.request(**request_kwargs)

            duration = time.time() - start_time
            metrics_collector.record_service_request(
                service_config.name, method, response.status_code, duration
            )

            structured_logger.log_service_call(
                service_config.name, method, target_url, response.status_code, duration
            )

            if response.status_code >= 400:
                try:
                    detail = response.json() if response.headers.get("content-type", "").startswith(APPLICATION_JSON) else response.text
                except Exception:
                    detail = response.text
                raise HTTPException(status_code=response.status_code, detail=detail)

            return (
                response.json()
                if response.headers.get("content-type", "").startswith(APPLICATION_JSON)
                else {"message": response.text}
            )

        except HTTPException:
            raise
        except Exception as e:
            duration = time.time() - start_time
            metrics_collector.record_service_request(service_config.name, method, 500, duration)
            structured_logger.log_service_call(service_config.name, method, target_url, 500, duration, str(e))
            raise e

    def _prepare_headers(self, request: Request) -> Dict[str, str]:
        """Prepare headers with automatic token forwarding."""
        headers = {
            "Content-Type": APPLICATION_JSON,
            "Accept": APPLICATION_JSON,
        }

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

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            headers["Authorization"] = auth_header

        return headers

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


service_client = ServiceClient()