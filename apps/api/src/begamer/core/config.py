from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from the repository-level ``.env`` file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )

    app_name: str = "BEGAMER API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v1"
    debug: bool = False

    database_url: str = "sqlite+aiosqlite:///./data/begamer.db"
    auto_create_database: bool = True
    seed_demo_data: bool = True

    frontend_origin: str = "http://localhost:5173"

    steam_web_api_key: str | None = None
    steam_id: str | None = None
    steam_api_base_url: str = "https://api.steampowered.com"

    openai_api_key: str | None = None
    openai_base_url: str | None = None
    openai_model: str = "gpt-5.6-luna"
    llm_timeout_seconds: float = Field(default=20.0, ge=1.0, le=120.0)


@lru_cache
def get_settings() -> Settings:
    return Settings()
