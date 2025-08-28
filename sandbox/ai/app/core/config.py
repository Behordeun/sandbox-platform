from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "AI Service"
    app_version: str = "1.0.0"
    debug: bool = False

    host: str = "0.0.0.0"
    port: int = 8002

    # AI API settings
    ai_api_key: str = ""
    ai_model: str = "gpt-3.5-turbo"
    ai_max_tokens: int = 2000

    model_config = ConfigDict(
        env_file="../../../../.env",  # Use root .env file
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from .env
    )


settings = Settings()
