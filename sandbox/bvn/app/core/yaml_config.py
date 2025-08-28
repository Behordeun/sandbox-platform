"""
YAML Configuration for BVN Service
"""

import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import sys
from pathlib import Path

# Add config directory to path
config_path = Path(__file__).parent.parent.parent.parent / "config"
sys.path.insert(0, str(config_path))

try:
    from config_loader import get_service_config, get_provider_config
except ImportError:
    # Fallback if config loader not available
    def get_service_config(_service, _env):
        return None
    def get_provider_config(_provider, _env):
        return None


class Settings(BaseSettings):
    """BVN Service Settings loaded from YAML configuration."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Load configuration from YAML
        environment = os.getenv("ENVIRONMENT", "development")
        service_config = get_service_config("bvn_service", environment)
        doja_config = get_provider_config("dojah", environment)
        
        # Apply YAML configuration
        if service_config:
            self.app_name = service_config.get("app_name", "BVN Verification Service")
            self.app_version = service_config.get("app_version", "1.0.0")
            self.debug = service_config.get("debug", False)
            self.host = service_config.get("host", "0.0.0.0")
            self.port = service_config.get("port", 8006)
            self.cache_ttl = service_config.get("cache_ttl", 3600)
        
        # Doja API Configuration
        if doja_config:
            self.dojah_api_key = doja_config.get("api_key", os.getenv("DOJAH_API_KEY"))
            self.dojah_app_id = doja_config.get("app_id", os.getenv("DOJAH_APP_ID"))
            self.dojah_base_url = doja_config.get("base_url", "https://api.dojah.io")
            self.dojah_timeout = doja_config.get("timeout", 30)
    
    # Default values
    app_name: str = "BVN Verification Service"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8006
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