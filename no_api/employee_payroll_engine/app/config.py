from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url:str
    debug:bool