"""VNBOT API — Application configuration.

Loads from .env via pydantic-settings. Validates at startup.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    NEVER hardcode secrets here. All sensitive values come from .env.
    .env.example documents all available variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ─── General ───
    vnbot_env: Literal["development", "staging", "production"] = "development"
    vnbot_base_url: str = "http://localhost:5173"
    vnbot_log_level: Literal["DEBUG", "INFO", "WARN", "ERROR"] = "INFO"

    # ─── Database ───
    database_url: str = "sqlite+aiosqlite:///./data/vnbot.db"

    # ─── Auth / Sessions ───
    session_secret: str = Field(default="CHANGE_ME", min_length=16)
    session_cookie_name: str = "vnbot_session"
    session_max_age_seconds: int = 86400

    # ─── Encryption ───
    encryption_key: str = Field(default="CHANGE_ME", min_length=16)
    encryption_key_version: int = 1

    # ─── LLM Provider ───
    llm_provider: Literal["auto", "zai", "ollama", "openai", "anthropic", "gemini"] = "auto"
    llm_zai_base_url: str = "https://api.z.ai/v1"
    llm_zai_model: str = "glm-4.6"
    llm_zai_rate_limit_rpm: int = 30
    llm_api_key: str | None = None  # NOT needed for Z.AI

    # ─── Scheduler ───
    scheduler_lookahead_days: int = 30
    scheduler_tick_seconds: int = 60
    scheduler_timezone: str = "America/Caracas"

    # ─── Observability ───
    otel_exporter_otlp_endpoint: str = ""  # empty = console exporter
    otel_service_name: str = "vnbot-api"
    otel_resource_attributes: str = "vnbot.env=development"

    # ─── Notifications ───
    notification_channel_default: Literal["mock", "web_push", "email"] = "mock"

    # ─── File storage ───
    storage_backend: Literal["local", "s3"] = "local"
    storage_local_path: str = "./data/files"

    @property
    def is_dev(self) -> bool:
        return self.vnbot_env == "development"

    @property
    def is_production(self) -> bool:
        return self.vnbot_env == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
