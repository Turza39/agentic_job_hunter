"""
Application configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    postgres_user: str = "jobagent"
    postgres_password: str = "turza039"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "job_agent"
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False
    
    # File uploads
    cv_upload_dir: str = "cv-storage/uploads"
    max_cv_size_mb: int = 10
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
