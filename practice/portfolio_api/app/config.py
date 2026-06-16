from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str
    api_key: str
    max_requests_per_minute: int = 10
    app_name: str = "portfolio API"
    app_version: str = "1.0.0"
    debug: bool = False

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()