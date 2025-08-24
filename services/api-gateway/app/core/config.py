import os
from typing import Dict, List

from pydantic_settings import BaseSettings

HEALTH_PATH = "/health"

HEALTH_PATH = "/health"

class ServiceConfig(BaseSettings):
    """Configuration for a backend service."""

    name: str
    url: str
    health_path: str = HEALTH_PATH
    timeout: int = 30
    retries: int = 3
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 60


class Settings(BaseSettings):
    # Application settings
    app_name: str = "Sandbox API Gateway"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8080

    # CORS settings
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    cors_allow_credentials: bool = False
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds

    # Redis settings (for rate limiting and caching)
    redis_url: str = "redis://localhost:6379/0"

    # JWT settings for token validation
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"

    # Service URLs
    auth_service_url: str = "http://localhost:8000"
    config_service_url: str = "http://localhost:8001"
    auth_service_timeout: int = 30
    services: Dict[str, ServiceConfig] = {
        "auth": ServiceConfig(
            name="auth-service", url="http://auth-service:8000", health_path=HEALTH_PATH
        ),
        "sms": ServiceConfig(
            name="sms-service", url="http://sms-service:8000", health_path=HEALTH_PATH
        ),
        "llm": ServiceConfig(
            name="llm-service", url="http://llm-service:8000", health_path=HEALTH_PATH
        ),
        "nin": ServiceConfig(
            name="nin-service", url="http://nin-service:8005", health_path=HEALTH_PATH
        ),
        "bvn": ServiceConfig(
            name="bvn-service", url="http://bvn-service:8006", health_path=HEALTH_PATH
        ),
    }

    # Load balancing
    load_balancing_strategy: str = (
        "round_robin"  # round_robin, least_connections, random
    )

    # Circuit breaker settings
    circuit_breaker_enabled: bool = True
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout: int = 60
    circuit_breaker_expected_recovery_time: int = 30

    # Monitoring and metrics
    metrics_enabled: bool = True
    metrics_path: str = "/metrics"

    # Request/Response logging
    request_logging_enabled: bool = True
    response_logging_enabled: bool = True

    # Timeout settings
    default_timeout: int = 30
    max_timeout: int = 300

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
jwt_secret = os.getenv("JWT_SECRET_KEY")
if jwt_secret is None:
    raise ValueError("JWT_SECRET_KEY environment variable is not set")
settings = Settings(jwt_secret_key=jwt_secret)
