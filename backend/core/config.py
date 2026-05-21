from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://biasharaiq_user:HNGUx7rn1527Utk6SAFtEffp7tUrI85z@dpg-d7p4gi5ckfvc73f23k20-a.oregon-postgres.render.com/biasharaiq")
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", 20))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", 10))
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production-min-32-chars")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    
    # API Configuration
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    IS_PRODUCTION: bool = ENVIRONMENT == "production"
    
    # API Keys
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Frontend Configuration
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "https://biashara-iq.vercel.app")
    
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "https://biashara-iq.vercel.app")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # M-Pesa Configuration
    MPESA_CONSUMER_KEY: str = os.getenv("MPESA_CONSUMER_KEY", "")
    MPESA_CONSUMER_SECRET: str = os.getenv("MPESA_CONSUMER_SECRET", "")
    MPESA_SHORTCODE: str = os.getenv("MPESA_SHORTCODE", "")
    MPESA_PASSKEY: str = os.getenv("MPESA_PASSKEY", "")
    MPESA_CALLBACK_URL: str = os.getenv("MPESA_CALLBACK_URL", "")
    MPESA_ENVIRONMENT: str = os.getenv("MPESA_ENVIRONMENT", "sandbox")  # sandbox or production

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
        extra = "ignore"


settings = Settings()
