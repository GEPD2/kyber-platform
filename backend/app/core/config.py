"""
Application settings loaded from environment variables via pydantic-settings.

ALLOWED_ORIGINS is declared as a plain str and split manually — pydantic-settings
tries to JSON-parse List[str] fields, which breaks comma-separated env values.
"""
import secrets
from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # App
    APP_NAME: str  = "CRYSTALS-Kyber Training"
    APP_ENV:  str  = "production"
    DEBUG:    bool = False

    # CORS
    # Declared as str, split in property below.
    # pydantic-settings JSON-parses List[str] fields, breaking comma-separated values.
    ALLOWED_ORIGINS_RAW: str = "http://localhost,http://localhost:80,http://127.0.0.1,http://127.0.0.1:80"

    @property
    def ALLOWED_ORIGINS(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS_RAW.split(",") if o.strip()]

    # JWT / Secrets
    SECRET_KEY:                  str = ""
    JWT_SECRET:                  str = ""
    JWT_ALGORITHM:               str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS:   int = 7

    @model_validator(mode="after")
    def ensure_secrets(self) -> "Settings":
        """Auto-generate secrets if missing so the container always starts."""
        placeholder = "CHANGE_ME"
        if not self.SECRET_KEY or placeholder in self.SECRET_KEY:
            object.__setattr__(self, "SECRET_KEY", secrets.token_hex(32))
        if not self.JWT_SECRET or placeholder in self.JWT_SECRET:
            object.__setattr__(self, "JWT_SECRET", secrets.token_hex(32))
        return self

    # MySQL
    DB_HOST:         str = "mysql"
    DB_PORT:         int = 3306
    MYSQL_USER:      str = "kyber_app"
    MYSQL_PASSWORD:  str = ""
    MYSQL_DATABASE:  str = "kyber_training"
    DB_POOL_SIZE:    int = 5
    DB_MAX_OVERFLOW: int = 10

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.MYSQL_DATABASE}"
            f"?charset=utf8mb4"
        )

    # Redis
    REDIS_HOST:     str = "redis"
    REDIS_PORT:     int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB:       int = 0

    # Security
    BCRYPT_ROUNDS:      int = 12
    MAX_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_MINUTES:    int = 15
    CSRF_TOKEN_EXPIRE:  int = 3600

    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW:   int = 60
    ANSWER_SUBMIT_LIMIT: int = 30

    # TLS
    TLS_ENABLED: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
