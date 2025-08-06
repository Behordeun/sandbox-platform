import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from typing import Callable

from app.core.config import settings

# Prometheus metrics
REQUEST_COUNT = Counter(
    'api_gateway_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'api_gateway_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_REQUESTS = Gauge(
    'api_gateway_active_requests',
    'Number of active requests'
)

SERVICE_REQUEST_COUNT = Counter(
    'api_gateway_service_requests_total',
    'Total number of service requests',
    ['service', 'method', 'status_code']
)

SERVICE_REQUEST_DURATION = Histogram(
    'api_gateway_service_request_duration_seconds',
    'Service request duration in seconds',
    ['service', 'method']
)

CIRCUIT_BREAKER_STATE = Gauge(
    'api_gateway_circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=open, 2=half_open)',
    ['service']
)

RATE_LIMIT_HITS = Counter(
    'api_gateway_rate_limit_hits_total',
    'Total number of rate limit hits',
    ['client_type']
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Metrics collection middleware for API Gateway."""
    
    def __init__(self, app):
        super().__init__(app)
        self.enabled = settings.metrics_enabled
    
    async def dispatch(self, request: Request, call_next: Callable):
        """Process request through metrics middleware."""
        if not self.enabled:
            return await call_next(request)
        
        # Skip metrics collection for metrics endpoint
        if request.url.path == settings.metrics_path:
            return await call_next(request)
        
        # Increment active requests
        ACTIVE_REQUESTS.inc()
        
        # Start timing
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Record metrics
            self._record_request_metrics(request, response, start_time)
            
            return response
            
        except Exception as e:
            # Record error metrics
            self._record_error_metrics(request, start_time)
            raise e
        finally:
            # Decrement active requests
            ACTIVE_REQUESTS.dec()
    
    def _record_request_metrics(self, request: Request, response, start_time: float):
        """Record request metrics."""
        duration = time.time() - start_time
        
        # Get endpoint (remove query parameters and path parameters)
        endpoint = self._normalize_endpoint(request.url.path)
        
        # Record request count
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            status_code=response.status_code
        ).inc()
        
        # Record request duration
        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=endpoint
        ).observe(duration)
    
    def _record_error_metrics(self, request: Request, start_time: float):
        """Record error metrics."""
        duration = time.time() - start_time
        endpoint = self._normalize_endpoint(request.url.path)
        
        # Record as 500 error
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            status_code=500
        ).inc()
        
        REQUEST_DURATION.labels(
            method=request.method,
            endpoint=endpoint
        ).observe(duration)
    
    def _normalize_endpoint(self, path: str) -> str:
        """Normalize endpoint path for metrics."""
        # Remove IDs and other variable parts
        import re
        
        # Replace UUIDs
        path = re.sub(r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/{id}', path)
        
        # Replace numeric IDs
        path = re.sub(r'/\d+', '/{id}', path)
        
        # Replace other common patterns
        path = re.sub(r'/[a-zA-Z0-9_-]{20,}', '/{token}', path)
        
        return path


class MetricsCollector:
    """Metrics collector for service calls and circuit breakers."""
    
    @staticmethod
    def record_service_request(
        service: str, 
        method: str, 
        status_code: int, 
        duration: float
    ):
        """Record service request metrics."""
        SERVICE_REQUEST_COUNT.labels(
            service=service,
            method=method,
            status_code=status_code
        ).inc()
        
        SERVICE_REQUEST_DURATION.labels(
            service=service,
            method=method
        ).observe(duration)
    
    @staticmethod
    def update_circuit_breaker_state(service: str, state: str):
        """Update circuit breaker state metric."""
        state_value = {
            'closed': 0,
            'open': 1,
            'half_open': 2
        }.get(state, 0)
        
        CIRCUIT_BREAKER_STATE.labels(service=service).set(state_value)
    
    @staticmethod
    def record_rate_limit_hit(client_type: str):
        """Record rate limit hit."""
        RATE_LIMIT_HITS.labels(client_type=client_type).inc()


def get_metrics():
    """Get Prometheus metrics."""
    return generate_latest()


# Global metrics collector
metrics_collector = MetricsCollector()

