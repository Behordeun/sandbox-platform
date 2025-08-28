import os
from typing import Optional, List, Union

from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator


class Settings(BaseSettings):
    # Application settings
    app_name: str = "Sandbox Auth Service"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database settings
    database_url: str = os.getenv("DATABASE_URL", "postgresql://sandbox_user:password@localhost:5432/sandbox_platform")

    # JWT settings
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change-this-secret-key-in-production")
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
            if not v or v == "*":
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
            if not v or v == "*":
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
            if not v or v == "*":
                return ["*"]
            return [item.strip() for item in v.split(',') if item.strip()]
        return ["*"]

    # App settings
    host: str = "0.0.0.0"
    port: int = 8000

    # Email settings
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: str = "noreply@dpi-sandbox.ng"
    smtp_from_name: str = "DPI Sandbox Platform"

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
    model_config = ConfigDict(
        env_file="../../.env",  # Use root .env file
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields from .env
    )


# Global settings instance
settings = Settings()
