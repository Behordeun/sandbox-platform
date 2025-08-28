"""
YAML Configuration for Config Service
"""

import os

from dotenv import load_dotenv
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

# Load environment variables from root .env file
load_dotenv("../../../.env")
import sys
from pathlib import Path

# Add config directory to path
config_path = Path(__file__).parent.parent.parent / "config"
sys.path.insert(0, str(config_path))

try:
    from config_loader import get_service_config
except ImportError:
    # Fallback if config loader not available
    def get_service_config(_service, _env):
        return None


class Settings(BaseSettings):
    """Config Service Settings loaded from YAML configuration."""

    # Default values
    app_name: str = "Config Service"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8001
    storage_type: str = "redis"
    encryption_key: str = ""
    versioning_enabled: bool = True

    # Redis URL for config storage
    redis_url: str = ""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Load from centralized environment variables
        if not self.redis_url:
            self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/1")
        if not self.encryption_key:
            self.encryption_key = os.getenv("CONFIG_ENCRYPTION_KEY", "")

        # Load configuration from YAML
        environment = os.getenv("ENVIRONMENT", "development")
        service_config = get_service_config("config_service", environment)

        # Apply YAML configuration
        if service_config:
            self.app_name = service_config.get("app_name", "Config Service")
            self.app_version = service_config.get("app_version", "1.0.0")
            self.debug = service_config.get("debug", False)
            self.host = service_config.get("host", "0.0.0.0")
            self.port = service_config.get("port", 8001)
            self.storage_type = service_config.get("storage_type", "redis")
            self.encryption_key = os.getenv(
                "CONFIG_ENCRYPTION_KEY"
            ) or service_config.get("encryption_key", "")
            self.versioning_enabled = service_config.get("versioning_enabled", True)

    model_config = ConfigDict(
        env_file="../../../.env",  # Use root .env file
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from .env
    )


settings = Settings()
