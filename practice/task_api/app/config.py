from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url:str
    api_key:str
    app_name:str="Tasks API"
    app_version:str="1.0.0"
    max_requests_per_min:int
    debug:bool
    
    class Config:
        env_file=".env"
        
@lru_cache()
def get_settings()->Settings:
    return Settings()