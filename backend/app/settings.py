from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.local", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI Court"
    app_env: str = "local"
    app_debug: bool = False
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    database_url: str = "postgresql+asyncpg://ai_court:ai_court@localhost:5432/ai_court"
    redis_url: str = "redis://localhost:6379/0"
    frontend_origin: str = "http://localhost:5173"
    pdf_base_url: str = "http://localhost:8000"
    pdf_storage_path: str = "storage/pdfs"
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    llm_mode: str = Field(default="mock", pattern="^(mock|live)$")
    embedding_dimensions: int = 1536
    rate_limit_per_minute: int = 60
    trial_step_delay_ms: int = Field(default=450, ge=0, le=5000)

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
