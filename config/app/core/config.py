from typing import List, Union

from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator


class Settings(BaseSettings):
    # Application settings
    app_name: str = "Sandbox Config Service"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS settings
    cors_origins: Union[str, List[str]] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: Union[str, List[str]] = ["*"]
    cors_allow_headers: Union[str, List[str]] = ["*"]
    
    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        if v is None or v == "":
            return ["*"]
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            if v == "*":
                return ["*"]
            return [item.strip() for item in v.split(',') if item.strip()]
        return ["*"]
    
    @field_validator('cors_allow_methods', mode='before')
    @classmethod
    def parse_cors_methods(cls, v):
        if v is None or v == "":
            return ["*"]
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            if v == "*":
                return ["*"]
            return [item.strip() for item in v.split(',') if item.strip()]
        return ["*"]
    
    @field_validator('cors_allow_headers', mode='before')
    @classmethod
    def parse_cors_headers(cls, v):
        if v is None or v == "":
            return ["*"]
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            v = v.strip()
            if v == "*":
                return ["*"]
            return [item.strip() for item in v.split(',') if item.strip()]
        return ["*"]

    # Redis settings (for caching and pub/sub)
    redis_url: str = "redis://localhost:6379/0"

    # Encryption settings
    encryption_key: str = "your-encryption-key-change-in-production"
    encryption_salt: str = "your-encryption-salt-change-in-production"

    # Configuration storage
    config_storage_type: str = "memory"  # memory, redis, file
    config_file_path: str = "/app/configs"

    # Environment management
    default_environment: str = "development"
    supported_environments: List[str] = ["development", "staging", "production"]

    # Configuration validation
    schema_validation_enabled: bool = True

    # Audit logging
    audit_logging_enabled: bool = True

    # Configuration versioning
    versioning_enabled: bool = True
    max_versions: int = 10

    # Hot reload settings
    hot_reload_enabled: bool = True
    reload_check_interval: int = 30  # seconds

    # Security settings
    api_key_required: bool = False
    jwt_secret_key: str = "your-jwt-secret-key"
    jwt_algorithm: str = "HS256"

    model_config = ConfigDict(
        env_file="../../../.env",  # Use root .env file
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields from .env
    )


# Global settings instance
settings = Settings()
