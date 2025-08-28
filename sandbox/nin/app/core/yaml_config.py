"""
YAML Configuration for NIN Service
"""

import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import sys
sys.path.append("../../../..")
from config.config_loader import get_service_config, get_provider_config


class Settings(BaseSettings):
    """NIN Service Settings loaded from YAML configuration."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Load configuration from YAML
        environment = os.getenv("ENVIRONMENT", "development")
        service_config = get_service_config("nin_service", environment)
        doja_config = get_provider_config("dojah", environment)
        
        # Apply YAML configuration
        if service_config:
            self.app_name = service_config.get("app_name", "NIN Verification Service")
            self.app_version = service_config.get("app_version", "1.0.0")
            self.debug = service_config.get("debug", False)
            self.host = service_config.get("host", "0.0.0.0")
            self.port = service_config.get("port", 8005)
            self.cache_ttl = service_config.get("cache_ttl", 3600)
        
        # Doja API Configuration
        if doja_config:
            self.dojah_api_key = doja_config.get("api_key", os.getenv("DOJAH_API_KEY"))
            self.dojah_app_id = doja_config.get("app_id", os.getenv("DOJAH_APP_ID"))
            self.dojah_base_url = doja_config.get("base_url", "https://api.dojah.io")
            self.dojah_timeout = doja_config.get("timeout", 30)
    
    # Default values
    app_name: str = "NIN Verification Service"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8005
    cache_ttl: int = 3600
    
    # Doja API
    dojah_api_key: str = ""
    dojah_app_id: str = ""
    dojah_base_url: str = "https://api.dojah.io"
    dojah_timeout: int = 30
    
    # Auth Service
    auth_service_url: str = "http://auth-service:8000"
    
    model_config = ConfigDict(
        env_file="../../../../.env",  # Use root .env file
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields from .env
    )


settings = Settings()