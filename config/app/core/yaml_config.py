"""
YAML Configuration for Config Service
"""

import os
from pydantic import BaseSettings
import sys
sys.path.append("../../..")
from config.config_loader import get_service_config


class Settings(BaseSettings):
    """Config Service Settings loaded from YAML configuration."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Load configuration from YAML
        environment = os.getenv("ENVIRONMENT", "development")
        service_config = get_service_config("config_service", environment)
        
        # Apply YAML configuration
        if service_config:
            self.app_name = service_config.get("app_name", "Config Service")
            self.app_version = service_config.get("app_version", "1.0.0")
            self.debug = service_config.get("debug", False)
            self.host = service_config.get("host", "0.0.0.0")
            self.port = service_config.get("port", 8001)
            self.storage_type = service_config.get("storage_type", "redis")
            self.encryption_key = service_config.get("encryption_key", os.getenv("CONFIG_ENCRYPTION_KEY"))
            self.versioning_enabled = service_config.get("versioning_enabled", True)
    
    # Default values
    app_name: str = "Config Service"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8001
    storage_type: str = "redis"
    encryption_key: str = ""
    versioning_enabled: bool = True
    
    # Redis URL for config storage
    redis_url: str = "redis://localhost:6379/1"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()