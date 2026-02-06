import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    APP_NAME: str = "PocketLedger"
    API_V1_PREFIX: str = "/api/v1"
    
    # Database (从环境变量读取)
    MYSQL_ROOT_PASSWORD: str = "rootpassword"
    MYSQL_USER: str = "pocketledger"
    MYSQL_PASSWORD: str = "password"
    MYSQL_DATABASE: str = "pocketledger"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@db:3306/{self.MYSQL_DATABASE}"
    
    # JWT
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Password
    PASSWORD_HASH_ALGORITHM: str = "bcrypt"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # 忽略未知的环境变量


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Create a global settings instance
settings = get_settings()
