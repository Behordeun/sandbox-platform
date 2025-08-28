from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "NIN Verification Service"
    app_version: str = "1.0.0"
    debug: bool = False

    host: str = "0.0.0.0"
    port: int = 8005

    # Dojah API settings
    dojah_api_key: str = ""
    dojah_app_id: str = ""
    dojah_base_url: str = "https://api.dojah.io"

    # Auth service URL for user updates
    auth_service_url: str = "http://auth-service:8000"

    model_config = ConfigDict(
        env_file="../../../../.env",  # Use root .env file
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from .env
    )


settings = Settings()
