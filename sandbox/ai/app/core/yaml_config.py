"""
Simplified Configuration for AI Service
"""

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """AI Service Settings loaded from environment variables."""

    # App Configuration
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
    auth_service_url: str = "http://127.0.0.1:8000"

    model_config = ConfigDict(
        env_file="../../../../.env",  # Use root .env file
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from .env
    )


settings = Settings()
