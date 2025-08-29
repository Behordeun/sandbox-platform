from typing import List, Optional, Union

from pydantic import ConfigDict, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application settings
    app_name: str = "Sandbox Auth Service"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database settings (required; no hard-coded default)
    database_url: str

    # JWT settings (required; no hard-coded default)
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # OAuth2 settings
    oauth2_issuer_url: str = "http://127.0.0.1:8000"
    oauth2_jwks_uri: str = "http://127.0.0.1:8000/.well-known/jwks.json"

    # NIN/BVN Integration settings
    doja_api_key: Optional[str] = None
    doja_base_url: str = "https://api.dojah.io"

    # CORS settings
    cors_origins: Union[str, List[str]] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: Union[str, List[str]] = ["*"]
    cors_allow_headers: Union[str, List[str]] = ["*"]

    @staticmethod
    def _parse_cors_value(v):
        import json

        if v is None or v == "":
            return ["*"]
        if isinstance(v, list):
            return [str(i).strip() for i in v if str(i).strip()]
        if isinstance(v, str):
            s = v.strip()
            if not s or s == "*":
                return ["*"]
            # Try JSON first
            try:
                parsed = json.loads(s)
                if isinstance(parsed, list):
                    return [str(i).strip() for i in parsed if str(i).strip()]
                return [str(parsed).strip()]
            except Exception:
                return [item.strip() for item in s.split(",") if item.strip()]
        return ["*"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        # Use helper for parsing CORS origins
        return cls._parse_cors_value(v)

    @field_validator("cors_allow_methods", mode="before")
    @classmethod
    def parse_cors_methods(cls, v):
        # Use helper for parsing CORS methods, but ensure only valid HTTP methods are returned if not wildcard
        parsed = cls._parse_cors_value(v)
        if "*" in parsed:
            return ["*"]
        valid_methods = [
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "PATCH",
            "OPTIONS",
            "HEAD",
            "TRACE",
            "CONNECT",
        ]
        return [method for method in parsed if method.upper() in valid_methods]

    @field_validator("cors_allow_headers", mode="before")
    @classmethod
    def parse_cors_headers(cls, v):
        # Use helper for parsing CORS headers
        return cls._parse_cors_value(v)

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
        env_file="../../../../.env",  # Use root .env file
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from .env
    )


# Global settings instance
settings = Settings()
