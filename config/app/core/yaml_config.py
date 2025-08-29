"""
YAML Configuration for Config Service
"""

import os
from typing import Any, List, Union

from dotenv import load_dotenv
from pydantic import ConfigDict, field_validator
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

    # CORS settings (tolerant to JSON or comma-separated strings)
    cors_origins: Union[str, List[str]] = ["*"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def validate_cors_origins(cls, v: Any) -> list:
        import json
        if v is None or v == "" or v == []:
            return ["*"]
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
                return [parsed]
            except Exception:
                # Fallback: comma-separated string
                return [i.strip() for i in v.split(",") if i.strip()]
        return ["*"]

    @classmethod
    def _validate_cors_origins(cls, value: Any):
        import json
        if value is None or value == "":
            return ["*"]
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return parsed
                return [parsed]
            except Exception:
                # Fallback: comma-separated string
                return [v.strip() for v in value.split(",") if v.strip()]
        return ["*"]

    cors_allow_credentials: bool = True
    cors_allow_methods: Union[str, List[str]] = ["*"]
    cors_allow_headers: Union[str, List[str]] = ["*"]

    @field_validator("cors_allow_methods", mode="before")
    @classmethod
    def validate_cors_methods(cls, v: Any) -> list:
        import json
        if v is None or v == "" or v == []:
            return ["*"]
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
                return [parsed]
            except Exception:
                return [i.strip() for i in v.split(",") if i.strip()]
        return ["*"]

    @field_validator("cors_allow_headers", mode="before")
    @classmethod
    def validate_cors_headers(cls, v: Any) -> list:
        import json
        if v is None or v == "" or v == []:
            return ["*"]
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
                return [parsed]
            except Exception:
                return [i.strip() for i in v.split(",") if i.strip()]
        return ["*"]

    @property
    def config_storage_type(self):
        # For backward compatibility with code expecting config_storage_type
        return self.storage_type

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Load from centralized environment variables
        if not self.redis_url:
            self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/1")
        if not self.encryption_key:
            self.encryption_key = os.getenv("CONFIG_ENCRYPTION_KEY", "")

        # Handle CORS origins from environment variable (supports JSON or comma-separated)
        cors_origins_env = os.getenv("CORS_ORIGINS", None)
        if cors_origins_env:
            import json
            try:
                self.cors_origins = json.loads(cors_origins_env)
                if not isinstance(self.cors_origins, list):
                    self.cors_origins = [self.cors_origins]
            except Exception:
                # Fallback: comma-separated string
                self.cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]

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
            # Load CORS config if present
            cors = service_config.get("cors", {})
            if "origins" in cors:
                self.cors_origins = cors.get("origins", ["*"])
            self.cors_allow_credentials = cors.get("allow_credentials", True)
            self.cors_allow_methods = cors.get("allow_methods", ["*"])
            self.cors_allow_headers = cors.get("allow_headers", ["*"])

    model_config = ConfigDict(
        env_file="../../../.env",  # Use root .env file
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from .env
    )


settings = Settings()
