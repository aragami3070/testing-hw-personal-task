"""Настройки запуска. Учётные данные хранятся только в .env."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    base_url: str = os.getenv("BASE_URL", "https://olmeko.ru").rstrip("/")
    email: str = os.getenv("TEST_EMAIL", "")
    password: str = os.getenv("TEST_PASSWORD", "")
    headless: bool = os.getenv("HEADLESS", "true").lower() in ("1", "true", "yes")
    timeout: int = int(os.getenv("TIMEOUT_MS", "15000"))
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()


config = Config()
