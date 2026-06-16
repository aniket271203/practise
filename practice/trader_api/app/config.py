from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str
    api_key: str
    max_requests_per_min: int
    app_name: str
    app_version: str
    debug: bool

    class Config:
        env_file = '.env'


@lru_cache()
def get_settings() -> Settings:
    return Settings()
