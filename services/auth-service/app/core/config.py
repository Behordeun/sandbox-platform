from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Application settings
    app_name: str = "Sandbox Auth Service"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database settings
    database_url: str = "postgresql://sandbox_user:changeme@localhost:5432/sandbox_auth"
    
    # JWT settings
    jwt_secret_key: str = "your-secret-key-change-in-production"
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
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

