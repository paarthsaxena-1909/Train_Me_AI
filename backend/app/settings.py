from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv(Path(__file__).resolve().parent / ".env")


DEFAULT_JWT_SECRET = "development-secret-change-me"
MIN_JWT_SECRET_LENGTH = 32
DEVELOPMENT_ENVIRONMENTS = frozenset({"development", "test", "testing"})
LogLevel = Literal["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]


class Settings(BaseSettings):
    app_name: str = "Train Me AI API"
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://trainme:trainme@postgres:5432/trainme"
    cors_origins: str = "http://localhost:5173"
    jwt_secret: str = DEFAULT_JWT_SECRET
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60
    upload_root: str = "/data/uploads"
    max_upload_bytes: int = 10 * 1024 * 1024
    app_timezone: str = "Asia/Kolkata"
    log_level: LogLevel = "INFO"

    model_config = SettingsConfigDict(extra="ignore")

    @field_validator("log_level", mode="before")
    @classmethod
    def validate_log_level(cls, value: object) -> str:
        if not isinstance(value, str):
            raise ValueError("LOG_LEVEL must be one of CRITICAL, ERROR, WARNING, INFO, or DEBUG")
        normalized = value.strip().upper()
        if normalized not in {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}:
            raise ValueError("LOG_LEVEL must be one of CRITICAL, ERROR, WARNING, INFO, or DEBUG")
        return normalized

    @model_validator(mode="after")
    def validate_jwt_secret(self) -> "Settings":
        environment = self.environment.strip().lower()
        if environment not in DEVELOPMENT_ENVIRONMENTS and (
            self.jwt_secret == DEFAULT_JWT_SECRET or len(self.jwt_secret) < MIN_JWT_SECRET_LENGTH
        ):
            raise ValueError(
                "JWT_SECRET must be at least 32 characters and must be overridden outside development/test"
            )
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
