"""
YAML Configuration for API Gateway
"""

import os
from typing import List
from pydantic import BaseSettings
import sys
sys.path.append("../../..")
from config.config_loader import get_service_config


class Settings(BaseSettings):
    """API Gateway Settings loaded from YAML configuration."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Load configuration from YAML
        environment = os.getenv("ENVIRONMENT", "development")
        service_config = get_service_config("api_gateway", environment)
        
        # Apply YAML configuration
        if service_config:
            self.app_name = service_config.get("app_name", "Sandbox API Gateway")
            self.app_version = service_config.get("app_version", "1.0.0")
            self.debug = service_config.get("debug", False)
            self.host = service_config.get("host", "0.0.0.0")
            self.port = service_config.get("port", 8080)
            self.auth_service_url = service_config.get("auth_service_url", "http://localhost:8000")
            self.redis_url = service_config.get("redis_url", "redis://localhost:6379/0")
            
            # Rate limiting configuration
            rate_config = service_config.get("rate_limiting", {})
            self.rate_limit_requests = rate_config.get("requests_per_minute", 100)
            self.rate_limit_window = rate_config.get("window_seconds", 60)
            
            # Circuit breaker configuration
            circuit_config = service_config.get("circuit_breaker", {})
            self.circuit_breaker_failure_threshold = circuit_config.get("failure_threshold", 5)
            self.circuit_breaker_recovery_timeout = circuit_config.get("recovery_timeout", 30)
            
            # Service URLs
            services = service_config.get("services", {})
            self.nin_service_url = services.get("nin_service", "http://localhost:8005")
            self.bvn_service_url = services.get("bvn_service", "http://localhost:8006")
            self.sms_service_url = services.get("sms_service", "http://localhost:8003")
            self.ai_service_url = services.get("ai_service", "http://localhost:8002")
            self.ivr_service_url = services.get("ivr_service", "http://localhost:8004")
            self.two_way_sms_service_url = services.get("two_way_sms_service", "http://localhost:8007")
    
    # Default values
    app_name: str = "Sandbox API Gateway"
    app_version: str = "1.0.0"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8080
    
    # Service URLs
    auth_service_url: str = "http://localhost:8000"
    redis_url: str = "redis://localhost:6379/0"
    nin_service_url: str = "http://localhost:8005"
    bvn_service_url: str = "http://localhost:8006"
    sms_service_url: str = "http://localhost:8003"
    ai_service_url: str = "http://localhost:8002"
    ivr_service_url: str = "http://localhost:8004"
    two_way_sms_service_url: str = "http://localhost:8007"
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    
    # Circuit Breaker
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout: int = 30
    
    # JWT
    jwt_secret_key: str = "${JWT_SECRET_KEY}"
    jwt_algorithm: str = "HS256"
    
    class Config:
        env_file = "../../../.env"  # Use root .env file
        case_sensitive = False


settings = Settings()