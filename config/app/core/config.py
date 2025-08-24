from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application settings
    app_name: str = "Sandbox Config Service"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000

    # CORS settings
    cors_origins: List[str] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

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

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
