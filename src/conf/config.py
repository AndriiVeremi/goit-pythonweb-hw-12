from pydantic_settings import BaseSettings
from pydantic import BaseModel, EmailStr, SecretStr, HttpUrl, Field
from typing import Optional, List
from pathlib import Path


class Settings(BaseSettings):
    # Database settings
    POSTGRES_DB: str = "hw7_db"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "123456"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    DB_URL: str = "postgresql+asyncpg://postgres:123456@localhost:5432/hw7_db"
    test_database_url: str = (
        "postgresql+asyncpg://postgres:123456@localhost:5432/hw7_test_db"
    )

    # Redis settings
    REDIS_URL: str = "redis://localhost"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # JWT settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"

    # Mail settings
    MAIL_USERNAME: str = "your-email@example.com"
    MAIL_PASSWORD: str = "your-email-password"
    MAIL_FROM: EmailStr = "your-email@example.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_FROM_NAME: str = "Your App Name"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    TEMPLATE_FOLDER: Path = Path(__file__).parent / "templates"

    # Cloudinary settings
    CLD_NAME: str = "your-cloud-name"
    CLD_API_KEY: int = 123456789
    CLD_API_SECRET: str = "your-api-secret"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


settings = Settings()
