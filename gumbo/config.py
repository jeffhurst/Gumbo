from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="llama3.1:8b", alias="OLLAMA_MODEL")
    ollama_timeout_seconds: int = Field(default=120, alias="OLLAMA_TIMEOUT_SECONDS")

    telegram_bot_token: str | None = Field(default=None, alias="TELEGRAM_BOT_TOKEN")

    gumbo_db_path: Path = Field(default=Path(".gumbo/gumbo.db"), alias="GUMBO_DB_PATH")
    gumbo_workspace_root: Path = Field(default=Path("."), alias="GUMBO_WORKSPACE_ROOT")
    gumbo_traces_path: Path = Field(default=Path(".gumbo/traces.jsonl"), alias="GUMBO_TRACES_PATH")

    web_search_provider: str = Field(default="duckduckgo", alias="WEB_SEARCH_PROVIDER")
    web_search_base_url: str = Field(default="https://duckduckgo.com/html/", alias="WEB_SEARCH_BASE_URL")

    shell_timeout_seconds: int = Field(default=45, alias="SHELL_TIMEOUT_SECONDS")
    shell_confirm_dangerous: bool = Field(default=False, alias="SHELL_CONFIRM_DANGEROUS")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
