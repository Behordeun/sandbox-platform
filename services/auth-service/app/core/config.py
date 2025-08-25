import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application settings
    app_name: str = "Sandbox Auth Service"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database settings
    database_url: Optional[str] = os.getenv('DATABASE_URL')

    # JWT settings
    jwt_secret_key: Optional[str] = os.getenv('JWT_SECRET_KEY')
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # OAuth2 settings
    oauth2_issuer_url: str = "http://localhost:8000"
    oauth2_jwks_uri: str = "http://localhost:8000/.well-known/jwks.json"

    # NIN/BVN Integration settings
    doja_api_key: Optional[str] = None
    doja_base_url: str = "https://api.dojah.io"

    # CORS settings
    cors_origins: list = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["*"]
    cors_allow_headers: list = ["*"]

    # App settings
    host: str = "0.0.0.0"
    port: int = 8000

    # Logging settings
    log_level: str = "info"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Security settings
    enable_oauth2: bool = True
    enable_nin_bvn_integration: bool = False

    # Environment management
    default_environment: str = "development"
    supported_environments: list = ["development", "staging", "production"]

    # Server settings
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
