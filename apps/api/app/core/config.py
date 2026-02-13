"""Application configuration"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@127.0.0.1:5433/apibridge"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # Clerk
    clerk_secret_key: str = ""
    clerk_webhook_secret: str = ""
    
    # OpenAI
    openai_api_key: str = ""
    
    # Rate Limiting
    default_rate_limit_per_day: int = 100
    
    # Environment
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
