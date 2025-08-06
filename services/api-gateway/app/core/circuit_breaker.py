import time
import asyncio
from enum import Enum
from typing import Dict, Callable, Any
from dataclasses import dataclass, field
from .config import settings


class CircuitBreakerState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerStats:
    """Statistics for circuit breaker."""
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: float = 0
    last_success_time: float = 0
    total_requests: int = 0


class CircuitBreaker:
    """Circuit breaker implementation for service calls."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_recovery_time: int = 30,
        name: str = "default"
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_recovery_time = expected_recovery_time
        self.name = name
        
        self.state = CircuitBreakerState.CLOSED
        self.stats = CircuitBreakerStats()
        self._lock = asyncio.Lock()
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection."""
        async with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitBreakerState.HALF_OPEN
                else:
                    raise CircuitBreakerOpenException(
                        f"Circuit breaker '{self.name}' is OPEN"
                    )
        
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as e:
            await self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt to reset."""
        return (
            time.time() - self.stats.last_failure_time 
            >= self.recovery_timeout
        )
    
    async def _on_success(self):
        """Handle successful call."""
        async with self._lock:
            self.stats.success_count += 1
            self.stats.total_requests += 1
            self.stats.last_success_time = time.time()
            
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.CLOSED
                self.stats.failure_count = 0
    
    async def _on_failure(self):
        """Handle failed call."""
        async with self._lock:
            self.stats.failure_count += 1
            self.stats.total_requests += 1
            self.stats.last_failure_time = time.time()
            
            if (
                self.stats.failure_count >= self.failure_threshold
                and self.state == CircuitBreakerState.CLOSED
            ):
                self.state = CircuitBreakerState.OPEN
    
    def get_state(self) -> CircuitBreakerState:
        """Get current circuit breaker state."""
        return self.state
    
    def get_stats(self) -> CircuitBreakerStats:
        """Get circuit breaker statistics."""
        return self.stats


class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open."""
    pass


class CircuitBreakerManager:
    """Manages circuit breakers for different services."""
    
    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
    
    def get_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for service."""
        if service_name not in self._breakers:
            self._breakers[service_name] = CircuitBreaker(
                failure_threshold=settings.circuit_breaker_failure_threshold,
                recovery_timeout=settings.circuit_breaker_recovery_timeout,
                expected_recovery_time=settings.circuit_breaker_expected_recovery_time,
                name=service_name
            )
        return self._breakers[service_name]
    
    def get_all_breakers(self) -> Dict[str, CircuitBreaker]:
        """Get all circuit breakers."""
        return self._breakers.copy()


# Global circuit breaker manager
circuit_breaker_manager = CircuitBreakerManager()

