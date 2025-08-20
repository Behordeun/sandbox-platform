import asyncio
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

from app.core.config import settings
from app.services.proxy import proxy_service


@dataclass
class ServiceInstance:
    """Represents a service instance."""

    name: str
    url: str
    health_path: str
    last_health_check: float
    is_healthy: bool
    response_time: float
    failure_count: int


class ServiceDiscovery:
    """Service discovery and load balancing."""

    def __init__(self):
        self.services: Dict[str, List[ServiceInstance]] = {}
        self.health_check_interval = 30  # seconds
        self.max_failures = 3
        self._round_robin_counters: Dict[str, int] = {}
        self._initialize_services()

    def _initialize_services(self):
        """Initialize services from configuration."""
        for service_name, config in settings.services.items():
            instance = ServiceInstance(
                name=service_name,
                url=config.url,
                health_path=config.health_path,
                last_health_check=0,
                is_healthy=True,
                response_time=0,
                failure_count=0,
            )
            self.services[service_name] = [instance]

    def get_service_instance(self, service_name: str) -> Optional[ServiceInstance]:
        """Get a healthy service instance using load balancing."""
        instances = self.services.get(service_name, [])
        healthy_instances = [i for i in instances if i.is_healthy]

        if not healthy_instances:
            # Return any instance if none are healthy
            return instances[0] if instances else None

        # Load balancing strategy
        if settings.load_balancing_strategy == "round_robin":
            return self._round_robin_selection(healthy_instances)
        elif settings.load_balancing_strategy == "least_connections":
            return self._least_response_time_selection(healthy_instances)
        elif settings.load_balancing_strategy == "random":
            return self._random_selection(healthy_instances)
        else:
            return healthy_instances[0]

    def _round_robin_selection(
        self, instances: List[ServiceInstance]
    ) -> ServiceInstance:
        """Round-robin load balancing."""
        service_name = instances[0].name
        if service_name not in self._round_robin_counters:
            self._round_robin_counters[service_name] = 0
        
        index = self._round_robin_counters[service_name] % len(instances)
        self._round_robin_counters[service_name] += 1
        return instances[index]

    def _least_response_time_selection(
        self, instances: List[ServiceInstance]
    ) -> ServiceInstance:
        """Select instance with lowest response time."""
        return min(instances, key=lambda x: x.response_time)

    def _random_selection(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """Random selection."""
        import random

        return random.choice(instances)

    async def health_check_all_services(self):
        """Perform health checks on all service instances."""
        tasks = []
        for service_name, instances in self.services.items():
            for instance in instances:
                if (
                    time.time() - instance.last_health_check
                    > self.health_check_interval
                ):
                    tasks.append(self._health_check_instance(instance))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _health_check_instance(self, instance: ServiceInstance):
        """Perform health check on a single instance."""
        try:
            start_time = time.time()
            result = await proxy_service.health_check_service(instance.name)
            response_time = time.time() - start_time

            instance.last_health_check = time.time()
            instance.response_time = response_time

            if result["status"] == "healthy":
                instance.is_healthy = True
                instance.failure_count = 0
            else:
                instance.failure_count += 1
                if instance.failure_count >= self.max_failures:
                    instance.is_healthy = False

        except Exception:
            instance.failure_count += 1
            instance.last_health_check = time.time()
            if instance.failure_count >= self.max_failures:
                instance.is_healthy = False

    def add_service_instance(
        self, service_name: str, url: str, health_path: str = "/health"
    ):
        """Add a new service instance."""
        instance = ServiceInstance(
            name=service_name,
            url=url,
            health_path=health_path,
            last_health_check=0,
            is_healthy=True,
            response_time=0,
            failure_count=0,
        )

        if service_name not in self.services:
            self.services[service_name] = []

        self.services[service_name].append(instance)

    def remove_service_instance(self, service_name: str, url: str):
        """Remove a service instance."""
        if service_name in self.services:
            self.services[service_name] = [
                i for i in self.services[service_name] if i.url != url
            ]

    def get_service_status(self) -> Dict[str, Dict]:
        """Get status of all services."""
        status = {}
        for service_name, instances in self.services.items():
            healthy_count = sum(1 for i in instances if i.is_healthy)
            total_count = len(instances)

            status[service_name] = {
                "total_instances": total_count,
                "healthy_instances": healthy_count,
                "instances": [
                    {
                        "url": i.url,
                        "is_healthy": i.is_healthy,
                        "response_time": i.response_time,
                        "failure_count": i.failure_count,
                        "last_health_check": i.last_health_check,
                    }
                    for i in instances
                ],
            }

        return status


# Global service discovery instance
service_discovery = ServiceDiscovery()
