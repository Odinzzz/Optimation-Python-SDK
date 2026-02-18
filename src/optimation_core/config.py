# src\optimation_core\config.py

from __future__ import annotations

import os
from dataclasses import dataclass

from .exceptions import ConfigError


def _env(name: str, default: str | None = None) -> str | None:
    val = os.getenv(name, default)
    if val is None:
        return None
    val = val.strip()
    return val if val else None


def require_env(name: str) -> str:
    val = _env(name)
    if not val:
        raise ConfigError(f"Missing environment variable: {name}")
    return val


@dataclass(frozen=True)
class Settings:
    """
    Settings globaux Optimation (tu peux agrandir au fil du temps).
    """
    env: str = "dev"
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            env=_env("OPTIMATION_ENV", "dev") or "dev",
            log_level=_env("OPTIMATION_LOG_LEVEL", "INFO") or "INFO",
        )
