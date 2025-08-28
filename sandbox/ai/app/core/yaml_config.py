"""
YAML Configuration for AI Service
"""

import os
import sys

from pydantic import ConfigDict
from pydantic_settings import BaseSettings

sys.path.append("../../../..")
from config.config_loader import get_provider_config, get_service_config


class Settings(BaseSettings):
    """AI Service Settings loaded from YAML configuration."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Load configuration from YAML
        environment = os.getenv("ENVIRONMENT", "development")
        service_config = get_service_config("ai_service", environment)
        ai_config = get_provider_config("ai", environment)

        # Apply YAML configuration
        if service_config:
            self.app_name = service_config.get("app_name", "AI Service")
            self.app_version = service_config.get("app_version", "1.0.0")
            self.debug = service_config.get("debug", False)
            self.host = service_config.get("host", "0.0.0.0")
            self.port = service_config.get("port", 8002)
            self.nigerian_context = service_config.get("nigerian_context", True)
            self.default_currency = service_config.get("default_currency", "NGN")
            self.default_location = service_config.get("default_location", "Nigeria")

        # AI Provider Configuration
        if ai_config:
            self.ai_provider = ai_config.get("provider", "openai")
            self.ai_api_key = ai_config.get("api_key", os.getenv("AI_API_KEY"))
            self.ai_model = ai_config.get("model", "gpt-3.5-turbo")
            self.ai_max_tokens = ai_config.get("max_tokens", 2000)

    # Default values
    app_name: str = "AI Service"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8002
    nigerian_context: bool = True
    default_currency: str = "NGN"
    default_location: str = "Nigeria"

    # AI Provider
    ai_provider: str = "openai"
    ai_api_key: str = ""
    ai_model: str = "gpt-3.5-turbo"
    ai_max_tokens: int = 2000

    # Auth Service
    auth_service_url: str = "http://auth-service:8000"

    model_config = ConfigDict(
        env_file="../../../../.env",  # Use root .env file
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from .env
    )


settings = Settings()
