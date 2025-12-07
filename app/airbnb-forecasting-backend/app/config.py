"""
Application configuration and settings.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Airbnb LA Forecasting"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/airbnb_forecasting.db"
    
    # Model paths
    MODELS_DIR: str = "data/models"
    DATA_DIR: str = "data"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
