from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Config Service"
    app_version: str = "1.0.0"
    debug: bool = False

    host: str = "0.0.0.0"
    port: int = 8001

    # Storage settings
    storage_type: str = "redis"
    redis_url: str = "redis://localhost:6379/1"
    encryption_key: str = ""
    versioning_enabled: bool = True

    model_config = ConfigDict(
        env_file="../../../.env",  # Use root .env file
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from .env
    )


settings = Settings()