import asyncio
from typing import Dict, List, Any
from datetime import datetime

from app.core.config import settings
from app.core.circuit_breaker import circuit_breaker_manager
from app.services.proxy import proxy_service


class HealthService:
    """Service for health checking and monitoring."""
    
    def __init__(self):
        self.last_check_time = None
        self.cached_health_status = {}
        self.cache_duration = 30  # seconds
    
    async def get_gateway_health(self) -> Dict[str, Any]:
        """Get API Gateway health status."""
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.app_version,
            "uptime": self._get_uptime(),
            "services": await self.get_services_health(),
            "circuit_breakers": self.get_circuit_breaker_status()
        }
    
    async def get_services_health(self) -> Dict[str, Any]:
        """Get health status of all backend services."""
        # Check if we have cached results
        if (
            self.last_check_time and 
            (datetime.utcnow() - self.last_check_time).seconds < self.cache_duration
        ):
            return self.cached_health_status
        
        # Perform health checks
        health_checks = []
        for service_name in settings.services.keys():
            health_checks.append(
                proxy_service.health_check_service(service_name)
            )
        
        # Execute health checks concurrently
        results = await asyncio.gather(*health_checks, return_exceptions=True)
        
        # Process results
        services_health = {}
        overall_status = "healthy"
        
        for i, result in enumerate(results):
            service_name = list(settings.services.keys())[i]
            
            if isinstance(result, Exception):
                services_health[service_name] = {
                    "service": service_name,
                    "status": "error",
                    "error": str(result)
                }
                overall_status = "degraded"
            else:
                services_health[service_name] = result
                if result["status"] != "healthy":
                    overall_status = "degraded"
        
        # Cache results
        self.cached_health_status = {
            "overall_status": overall_status,
            "services": services_health,
            "last_check": datetime.utcnow().isoformat()
        }
        self.last_check_time = datetime.utcnow()
        
        return self.cached_health_status
    
    def get_circuit_breaker_status(self) -> Dict[str, Any]:
        """Get circuit breaker status for all services."""
        breakers = circuit_breaker_manager.get_all_breakers()
        status = {}
        
        for service_name, breaker in breakers.items():
            stats = breaker.get_stats()
            status[service_name] = {
                "state": breaker.get_state().value,
                "failure_count": stats.failure_count,
                "success_count": stats.success_count,
                "total_requests": stats.total_requests,
                "last_failure_time": stats.last_failure_time,
                "last_success_time": stats.last_success_time
            }
        
        return status
    
    def _get_uptime(self) -> str:
        """Get gateway uptime (placeholder implementation)."""
        # In a real implementation, this would track actual uptime
        return "unknown"
    
    async def check_service_connectivity(self, service_name: str) -> bool:
        """Check if a specific service is reachable."""
        try:
            result = await proxy_service.health_check_service(service_name)
            return result["status"] == "healthy"
        except Exception:
            return False
    
    def get_service_metrics(self, service_name: str) -> Dict[str, Any]:
        """Get metrics for a specific service."""
        breaker = circuit_breaker_manager.get_breaker(service_name)
        stats = breaker.get_stats()
        
        return {
            "service": service_name,
            "circuit_breaker": {
                "state": breaker.get_state().value,
                "failure_count": stats.failure_count,
                "success_count": stats.success_count,
                "total_requests": stats.total_requests,
                "failure_rate": (
                    stats.failure_count / max(stats.total_requests, 1)
                ) * 100
            }
        }


# Global health service instance
health_service = HealthService()

