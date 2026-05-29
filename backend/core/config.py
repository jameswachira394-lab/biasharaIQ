from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path
from dotenv import load_dotenv

# Load .env file explicitly at module level
backend_dir = Path(__file__).parent.parent
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://localhost/biasharaiq"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    
    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    
    # API Configuration
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    IS_PRODUCTION: bool = False
    
    # API Keys
    GEMINI_API_KEY: str = ""
    POLLINATIONS_API_KEY: str = ""
    CLOUDINARY_URL: str = ""  # cloudinary://key:secret@cloud_name

    # Veryfi Lens document parser credentials
    CLIENT_ID: str = ""
    CLIENT_SECRET: str = ""
    CLIENT_API: str = ""
    CLIENT_USERNAME: str = ""
    
    # Frontend Configuration
    FRONTEND_URL: str = "https://biashara-iq.vercel.app"
    
    CORS_ORIGINS: str = "https://biashara-iq.vercel.app"
    
    # Logging
    LOG_LEVEL: str = "INFO"

    # M-Pesa Configuration
    MPESA_CONSUMER_KEY: str = ""
    MPESA_CONSUMER_SECRET: str = ""
    MPESA_SHORTCODE: str = ""
    MPESA_PASSKEY: str = ""
    MPESA_CALLBACK_URL: str = ""
    MPESA_ENVIRONMENT: str = "sandbox"


    @property
    def cors_origins_list(self) -> List[str]:
        origins = [o.strip() for o in self.CORS_ORIGINS.split(",")]
        # Prevent wildcard in production
        if not self.DEBUG and "*" in origins:
            raise ValueError("Wildcard CORS not allowed in production")
        return origins

    def model_post_init(self, __context):
        """Update DEBUG and IS_PRODUCTION based on ENVIRONMENT"""
        object.__setattr__(self, 'DEBUG', self.ENVIRONMENT == "development")
        object.__setattr__(self, 'IS_PRODUCTION', self.ENVIRONMENT == "production")
        
        # Dynamically build DATABASE_URL if not set in env
        import os
        if not os.getenv("DATABASE_URL") or self.DATABASE_URL == "postgresql://localhost/biasharaiq":
            db_user = os.getenv("DB_USER")
            db_pass = os.getenv("DB_PASSWORD")
            db_host = os.getenv("DB_HOST")
            db_port = os.getenv("DB_PORT", "5432")
            db_name = os.getenv("DB_NAME")
            if db_user and db_pass and db_host and db_name:
                object.__setattr__(
                    self, 
                    'DATABASE_URL', 
                    f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
                )

    class Config:
        env_file = backend_dir / ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()
