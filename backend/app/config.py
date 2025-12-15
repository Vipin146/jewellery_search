# backend/app/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    PRODUCTS_PATH: str = "backend/app/datasets/Search Products (2).xlsx"
    FALLBACK_THRESHOLD: float = 0.4

    class Config:
        env_prefix = "JS_"

settings = Settings()
