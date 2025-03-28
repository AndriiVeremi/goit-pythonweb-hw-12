from pydantic_settings import BaseSettings
from pydantic import ConfigDict, EmailStr


class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://postgres:123456@localhost:5432/hw7_db"
    # jwt
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"
    SECRET_KEY: str = "secret"
    # redis
    REDIS_URL: str = "redis://localhost"
    # mail
    MAIL_USERNAME: EmailStr = "example@ukr.net"
    MAIL_PASSWORD: str = "secretPassword"
    MAIL_FROM: EmailStr = "example@ukr.net"
    MAIL_PORT: int = 465
    MAIL_SERVER: str = "smtp.ukr.net"
    MAIL_FROM_NAME: str = "Rest API Service"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    #cloudinary
    CLD_NAME: str
    CLD_API_KEY: int = 191275896727463
    CLD_API_SECRET: str = "secret"

    model_config = ConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True, extra="ignore"
    )


settings = Settings()
