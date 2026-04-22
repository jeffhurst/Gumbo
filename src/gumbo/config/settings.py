from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    ollama_base_url: str
    ollama_model: str
    system_prompt: str
    log_level: str
    max_history_messages: int
    temperature: float
    telegram_boot_chat_id: Optional[int]


class SettingsError(ValueError):
    """Raised when environment configuration is invalid."""


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SettingsError(f"Missing required environment variable: {name}")
    return value


def _positive_int_env(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    try:
        value = int(raw_value)
    except ValueError as exc:
        raise SettingsError(f"{name} must be an integer") from exc

    if value <= 0:
        raise SettingsError(f"{name} must be > 0")
    return value


def _bounded_float_env(name: str, default: float, min_value: float, max_value: float) -> float:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default

    try:
        value = float(raw_value)
    except ValueError as exc:
        raise SettingsError(f"{name} must be a number") from exc

    if not min_value <= value <= max_value:
        raise SettingsError(f"{name} must be between {min_value} and {max_value}")
    return value


def _optional_int_env(name: str) -> Optional[int]:
    raw_value = os.getenv(name)
    if raw_value is None:
        return None

    try:
        return int(raw_value)
    except ValueError as exc:
        raise SettingsError(f"{name} must be an integer") from exc


def load_settings() -> Settings:
    load_dotenv()

    return Settings(
        telegram_bot_token=_required_env("TELEGRAM_BOT_TOKEN"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.2"),
        system_prompt=os.getenv("SYSTEM_PROMPT", "You are a helpful assistant."),
        log_level=os.getenv("BOT_LOG_LEVEL", "INFO").upper(),
        max_history_messages=_positive_int_env("MAX_HISTORY_MESSAGES", 12),
        temperature=_bounded_float_env("OLLAMA_TEMPERATURE", 0.4, 0.0, 2.0),
        telegram_boot_chat_id=_optional_int_env("TELEGRAM_BOOT_CHAT_ID"),
    )
