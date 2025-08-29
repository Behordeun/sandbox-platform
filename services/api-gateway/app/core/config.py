from typing import Dict, List, Union

from pydantic import ConfigDict, field_validator
from pydantic_settings import BaseSettings

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
    cors_origins: Union[str, List[str]] = [
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ]
    cors_allow_credentials: bool = False
    cors_allow_methods: Union[str, List[str]] = ["*"]
    cors_allow_headers: Union[str, List[str]] = ["*"]

    @staticmethod
    def _parse_list_like(v, default: List[str]):
        import json

        if v is None or v == "":
            return default
        if isinstance(v, list):
            return [str(i).strip() for i in v if str(i).strip()]
        if isinstance(v, str):
            s = v.strip()
            if s == "*":
                return ["*"]
            # Try JSON first
            try:
                parsed = json.loads(s)
                if isinstance(parsed, list):
                    return [str(i).strip() for i in parsed if str(i).strip()]
                return [str(parsed).strip()]
            except Exception:
                return [item.strip() for item in s.split(",") if item.strip()]
        return default

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        return cls._parse_list_like(
            v, ["http://127.0.0.1:3000", "http://127.0.0.1:8080"]
        )

    @field_validator("cors_allow_methods", mode="before")
    @classmethod
    def parse_cors_methods(cls, v):
        return cls._parse_list_like(v, ["*"])

    @field_validator("cors_allow_headers", mode="before")
    @classmethod
    def parse_cors_headers(cls, v):
        return cls._parse_list_like(v, ["*"])

    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds

    # Redis settings (for rate limiting and caching)
    redis_url: str = "redis://127.0.0.1:6379/0"

    # JWT settings for token validation
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"

    # Service URLs
    auth_service_url: str = "http://127.0.0.1:8000"
    config_service_url: str = "http://127.0.0.1:8001"
    auth_service_timeout: int = 30
    services: Dict[str, ServiceConfig] = {
        "auth": ServiceConfig(
            name="auth-service", url="http://127.0.0.1:8000", health_path=HEALTH_PATH
        ),
        "sms": ServiceConfig(
            name="sms-service", url="http://127.0.0.1:8003", health_path=HEALTH_PATH
        ),
        "ai": ServiceConfig(
            name="ai-service", url="http://127.0.0.1:8002", health_path=HEALTH_PATH
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

    model_config = ConfigDict(
        env_file="../../../../.env",  # Use root .env file
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from .env
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Allow container / env overrides for service URLs
        try:
            import os

            auth_url = os.getenv("AUTH_SERVICE_URL") or self.auth_service_url
            sms_url = os.getenv("SMS_SERVICE_URL") or "http://127.0.0.1:8003"
            ai_url = os.getenv("AI_SERVICE_URL") or "http://127.0.0.1:8002"

            if "auth" in self.services:
                self.services["auth"].url = auth_url
            if "sms" in self.services:
                self.services["sms"].url = sms_url
            if "ai" in self.services:
                self.services["ai"].url = ai_url
        except Exception:
            # Keep defaults if any issue occurs
            pass


# Global settings instance
settings = Settings()
