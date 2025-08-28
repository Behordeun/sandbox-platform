"""
YAML Configuration for Auth Service
Replaces the traditional config.py with YAML-based configuration
"""

import os
from typing import List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from dotenv import load_dotenv

# Load environment variables from root .env file
load_dotenv("../../.env")
import sys
from pathlib import Path

# Add config directory to path
config_path = Path(__file__).parent.parent.parent.parent / "config"
sys.path.insert(0, str(config_path))

try:
    from config_loader import get_service_config, get_config
except ImportError:
    # Fallback if config loader not available
    def get_service_config(_service, _env):
        return None
    def get_config(_env):
        return {}


class Settings(BaseSettings):
    """Auth Service Settings loaded from YAML configuration."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Load configuration from YAML
        environment = os.getenv("ENVIRONMENT", "development")
        service_config = get_service_config("auth_service", environment)
        
        # Apply YAML configuration
        if service_config:
            self.app_name = service_config.get("app_name", "Sandbox Auth Service")
            self.app_version = service_config.get("app_version", "1.0.0")
            self.debug = service_config.get("debug", False)
            self.host = service_config.get("host", "0.0.0.0")
            self.port = service_config.get("port", 8000)
            
            # JWT Configuration
            jwt_config = service_config.get("jwt", {})
            self.jwt_secret_key = jwt_config.get("secret_key", os.getenv("JWT_SECRET_KEY"))
            self.jwt_algorithm = jwt_config.get("algorithm", "HS256")
            self.jwt_access_token_expire_minutes = jwt_config.get("access_token_expire_minutes", 30)
            self.jwt_refresh_token_expire_days = jwt_config.get("refresh_token_expire_days", 7)
            
            # OAuth2 Configuration
            oauth2_config = service_config.get("oauth2", {})
            self.oauth2_issuer_url = oauth2_config.get("issuer_url", "http://localhost:8000")
            self.oauth2_jwks_uri = oauth2_config.get("jwks_uri", "http://localhost:8000/.well-known/jwks.json")
            
            # CORS Configuration
            cors_config = service_config.get("cors", {})
            self.cors_origins = cors_config.get("origins", ["*"])
            self.cors_allow_credentials = cors_config.get("allow_credentials", True)
            self.cors_allow_methods = cors_config.get("allow_methods", ["*"])
            self.cors_allow_headers = cors_config.get("allow_headers", ["*"])
            
            # Email Configuration
            email_config = service_config.get("email", {})
            self.smtp_host = email_config.get("smtp_host", os.getenv("SMTP_HOST"))
            self.smtp_port = email_config.get("smtp_port", 587)
            self.smtp_username = email_config.get("smtp_username", os.getenv("SMTP_USERNAME"))
            self.smtp_password = email_config.get("smtp_password", os.getenv("SMTP_PASSWORD"))
            self.smtp_from_email = email_config.get("from_email", "noreply@dpi-sandbox.ng")
            self.smtp_from_name = email_config.get("from_name", "DPI Sandbox Platform")
        
        # Database Configuration
        config = get_config(environment)
        db_config = config.get("database", {})
        if db_config:
            self.database_url = os.getenv("DATABASE_URL") or db_config.get("url", "postgresql://postgres:MUhammad__1234@localhost:5432/sandbox_platform")
            # Get table prefix for auth service
            table_prefixes = db_config.get("table_prefixes", {})
            self.table_prefix = table_prefixes.get("auth_service", "auth_")
        else:
            # Use centralized environment variables
            self.database_url = os.getenv("DATABASE_URL", "postgresql://postgres:MUhammad__1234@localhost:5432/sandbox_platform")
            self.table_prefix = "auth_"
    
    # Default values (fallback if YAML config is not available)
    app_name: str = "Sandbox Auth Service"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str = "postgresql://sandbox_user:password@localhost:5432/sandbox_platform"
    table_prefix: str = "auth_"
    
    # JWT
    jwt_secret_key: str = "change-this-secret-key-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # OAuth2
    oauth2_issuer_url: str = "http://localhost:8000"
    oauth2_jwks_uri: str = "http://localhost:8000/.well-known/jwks.json"
    
    # CORS
    cors_origins: Union[str, List[str]] = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: Union[str, List[str]] = ["*"]
    cors_allow_headers: Union[str, List[str]] = ["*"]
    
    # Email
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: str = "noreply@dpi-sandbox.ng"
    smtp_from_name: str = "DPI Sandbox Platform"
    
    model_config = ConfigDict(
        env_file="../../.env",  # Use root .env file
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields from .env
    )


# Global settings instance
settings = Settings()