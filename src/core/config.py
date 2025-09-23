from functools import lru_cache
from pydantic_settings import BaseSettings
from clerk_backend_api import Clerk


class Settings(BaseSettings):
    # Database
    database_url: str

    # OpenAI
    open_ai_key: str

    # Clerk Authentication
    clerk_secret_key: str
    clerk_jwt_key: str
    clerk_authorized_parties: str
    clerk_webhook_secret: str

    # Application
    environment: str = "development"
    allowed_origins: str

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Initialize settings and Clerk SDK
settings = get_settings()
clerk_sdk = Clerk(bearer_auth=settings.clerk_secret_key)
