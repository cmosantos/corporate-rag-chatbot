from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    openai_api_key: str = Field(default="", repr=False)
    openai_model: str = "gpt-5.5"
    openai_vector_store_id: str = ""
    max_tool_rounds: int = 3
    audit_log_path: Path = Path("logs/audit.jsonl")

    internal_api_base_url: str = "https://internal-api.example.invalid"
    internal_api_token: str = Field(default="", repr=False)
    auth_shared_secret: str = Field(default="", repr=False)
    allowed_sensitivity_levels: str = "public,internal"

    @property
    def allowed_sensitivity_set(self) -> set[str]:
        return {level.strip().lower() for level in self.allowed_sensitivity_levels.split(",") if level}


@lru_cache
def get_settings() -> Settings:
    return Settings()

