from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost/biasharaiq"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    
    # API Configuration
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    
    # API Keys
    ANTHROPIC_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    
    
    CORS_ORIGINS: str = "http://localhost:3000"
    
    # Logging
    LOG_LEVEL: str = "INFO"

    @property
    def cors_origins_list(self) -> List[str]:
        origins = [o.strip() for o in self.CORS_ORIGINS.split(",")]
        # Prevent wildcard in production
        if not self.DEBUG and "*" in origins:
            raise ValueError("Wildcard CORS not allowed in production")
        return origins

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
