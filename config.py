"""
Application Configuration
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""

    # Application
    app_name: str = "SQL E-commerce Connector"
    app_version: str = "1.0.0"
    debug: bool = False

    # Database
    database_url: str = "sqlite:///./ecommerce_connector.db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Security
    secret_key: str = "change-this-secret-key-in-production"
    jwt_secret_key: str = "change-this-jwt-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    encryption_key: str = "change-this-encryption-key-32bytes"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    admin_port: int = 8001

    # Rate Limiting
    rate_limit_per_minute: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
