from typing import Any

from pydantic import ConfigDict, field_validator, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Config Service"
    app_version: str = "1.0.0"
    debug: bool = False

    host: str = "0.0.0.0"
    port: int = 8001

    # CORS settings
    cors_origins: list[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_allow_headers: list[str] = ["*"]

    @staticmethod
    def _parse_list_like(value: Any) -> list[str]:
        """Parse env values that may be JSON, comma-separated, or single string.

        Accepts:
        - JSON arrays (e.g., '["GET","POST"]')
        - Comma-separated strings (e.g., 'GET,POST')
        - Single string (e.g., '*')
        - None/empty -> ['*']
        """
        import json

        if value is None:
            return ["*"]
        if isinstance(value, list):
            return [str(v).strip() for v in value if str(v).strip()]
        if isinstance(value, str):
            v = value.strip()
            if v == "":
                return ["*"]
            # Try JSON first
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(i).strip() for i in parsed if str(i).strip()]
                # JSON scalar
                return [str(parsed).strip()]
            except Exception:
                # Fallback: comma-separated
                return [i.strip() for i in v.split(",") if i.strip()]
        # Fallback for unexpected types
        return ["*"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _validate_cors_origins(cls, v: Any) -> list[str]:
        return cls._parse_list_like(v)

    @field_validator("cors_allow_methods", mode="before")
    @classmethod
    def _validate_cors_methods(cls, v: Any) -> list[str]:
        return cls._parse_list_like(v)

    @field_validator("cors_allow_headers", mode="before")
    @classmethod
    def _validate_cors_headers(cls, v: Any) -> list[str]:
        return cls._parse_list_like(v)

    # Storage settings
    storage_type: str = "redis"
    config_storage_type: str = "redis"  # Alias for compatibility
    redis_url: str = "redis://localhost:6379/1"
    encryption_key: str = ""
    versioning_enabled: bool = True
    config_file_path: str = "./config_data"
    max_versions: int = 10

    @model_validator(mode="after")
    def _sync_storage_type(self):
        """If only CONFIG_STORAGE_TYPE is set in env, mirror to storage_type.

        This keeps compatibility with callers that read `storage_type` while
        allowing users to configure via CONFIG_STORAGE_TYPE.
        """
        # If storage_type wasn't explicitly set but config_storage_type was,
        # keep them aligned.
        if self.storage_type and self.config_storage_type and self.storage_type != self.config_storage_type:
            # Prefer explicit storage_type if provided; otherwise mirror.
            # Detect default by checking if storage_type is default 'redis' and
            # config_storage_type differs; in that case mirror from config_storage_type.
            if self.storage_type == "redis":
                self.storage_type = self.config_storage_type
        elif not self.storage_type and self.config_storage_type:
            self.storage_type = self.config_storage_type
        elif self.storage_type and not self.config_storage_type:
            self.config_storage_type = self.storage_type
        return self

    model_config = ConfigDict(
        env_file="../../../.env",  # Use root .env file
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from .env
    )


settings = Settings()
