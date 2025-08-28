from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "SMS Service"
    app_version: str = "1.0.0"
    debug: bool = False

    host: str = "0.0.0.0"
    port: int = 8003

    # SMS API settings
    sms_api_key: str = ""
    sms_sender_id: str = "DPISandbox"
    sms_base_url: str = "https://api.ng.termii.com"

    model_config = ConfigDict(
        env_file="../../../../.env",  # Use root .env file
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from .env
    )


settings = Settings()
