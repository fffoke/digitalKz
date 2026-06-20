"""Конфигурация приложения — читается из переменных окружения (.env)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/tildes"
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 14  # 2 недели

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
