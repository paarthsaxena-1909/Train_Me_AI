from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv(Path(__file__).resolve().parent / ".env")


class Settings(BaseSettings):
    app_name: str = "Train Me AI API"
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://trainme:trainme@postgres:5432/trainme"
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
