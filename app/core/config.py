from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field, validator
from typing import Optional
import logging

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    All settings can be overridden via .env file or environment variables.
    """
    
    PROJECT_NAME: str = "To Do Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database settings
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "todo"
    DATABASE_URL: Optional[str] = None
    TEST_DATABASE_URL: Optional[str] = None

    # Security settings
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    TEST_MODE: bool = True

    @validator("SECRET_KEY")
    def validate_secret_key(cls, v: str) -> str:
        """Validates that the secret key is long enough"""
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    @validator("ACCESS_TOKEN_EXPIRE_MINUTES")
    def validate_access_token_expire(cls, v: int) -> int:
        """Validates that access token lifetime is within reasonable limits"""
        if not 1 <= v <= 1440:  # from 1 minute to 24 hours
            raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be between 1 and 1440")
        return v

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

# Create global settings instance
settings = Settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)