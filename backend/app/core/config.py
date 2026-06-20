"""Конфигурация приложения — читается из переменных окружения (.env)."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/tildes"
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 14  # 2 недели

    # --- LLM (AI-собеседник) ---
    # provider: "stub" (заглушки) | "ollama" (локальная KazLLM) | "openai" (облако)
    LLM_PROVIDER: str = "stub"
    LLM_BASE_URL: str = "http://localhost:11434"
    LLM_MODEL: str = "issai/llama-3.1-kazllm-1.0-8b"

    # --- STT (распознавание речи) ---
    # provider: "local" (faster-whisper) | "openai" (gpt-4o-transcribe, облако)
    STT_PROVIDER: str = "local"

    # --- OpenAI (общий ключ для LLM и STT, если используем облако) ---
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4o-mini"            # дёшево и хорошо для диалога/оценки
    OPENAI_STT_MODEL: str = "gpt-4o-transcribe"  # дёшево, качество выше whisper

    # токен HuggingFace — для скачивания моделей (whisper, KazLLM)
    HF_TOKEN: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
