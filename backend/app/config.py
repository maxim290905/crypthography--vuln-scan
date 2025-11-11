from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://cryptscan:cryptscan_pass@localhost:5432/cryptscan_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    # Application
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    # Storage
    STORAGE_PATH: str = "/app/storage"
    REPORT_RETENTION_DAYS: int = 30
    
    # Scan settings
    SCAN_TIMEOUT_SECONDS: int = 300
    MAX_CONCURRENT_SCANS: int = 3
    
    # Security
    ALLOWED_TARGETS: Optional[str] = None  # Comma-separated list of allowed domains/IPs
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


