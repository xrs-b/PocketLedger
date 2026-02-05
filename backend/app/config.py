import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "PocketLedger"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/pocketledger"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Password
    PASSWORD_HASH_ALGORITHM: str = "bcrypt"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Create a global settings instance
settings = get_settings()
