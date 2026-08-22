"""
Application configuration
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # Database
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: int
    postgres_db: str

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False

    # File uploads
    cv_upload_dir: str = "cv-storage/uploads"
    max_cv_size_mb: int = 10

    model_config = SettingsConfigDict(
        env_file="/app/api/.env",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()