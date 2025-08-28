"""
YAML Configuration for SMS Service
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
    """SMS Service Settings loaded from YAML configuration."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Load configuration from YAML
        environment = os.getenv("ENVIRONMENT", "development")
        service_config = get_service_config("sms_service", environment)
        sms_config = get_provider_config("sms", environment)
        
        # Apply YAML configuration
        if service_config:
            self.app_name = service_config.get("app_name", "SMS Service")
            self.app_version = service_config.get("app_version", "1.0.0")
            self.debug = service_config.get("debug", False)
            self.host = service_config.get("host", "0.0.0.0")
            self.port = service_config.get("port", 8003)
            self.rate_limit = service_config.get("rate_limit", 100)
            self.daily_limit = service_config.get("daily_limit", 10000)
        
        # SMS Provider Configuration
        if sms_config:
            self.sms_provider = sms_config.get("provider", "termii")
            self.sms_api_key = os.getenv("SMS_API_KEY") or sms_config.get("api_key", "")
            self.sms_sender_id = sms_config.get("sender_id", "DPISandbox")
            self.sms_base_url = sms_config.get("base_url", "https://api.ng.termii.com")
    
    # Default values
    app_name: str = "SMS Service"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8003
    rate_limit: int = 100
    daily_limit: int = 10000
    
    # SMS Provider
    sms_provider: str = "termii"
    sms_api_key: str = ""
    sms_sender_id: str = "DPISandbox"
    sms_base_url: str = "https://api.ng.termii.com"
    
    # Auth Service
    auth_service_url: str = "http://auth-service:8000"
    
    model_config = ConfigDict(
        env_file="../../../../.env",  # Use root .env file
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields from .env
    )


settings = Settings()