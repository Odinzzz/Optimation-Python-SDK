from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional


class OptimationError(Exception):
    """Base de toutes les erreurs Optimation."""


class ConfigError(OptimationError):
    """Erreur de configuration (env manquante, mauvais format, etc.)."""


class ConnectorError(OptimationError):
    """Erreur provenant d'un connecteur (OpenAI, Google, ClickUp, etc.)."""


@dataclass(frozen=True)
class ApiError(ConnectorError):
    """
    Erreur HTTP standardisée pour un connecteur REST.
    - status_code=0: erreur réseau (pas de réponse HTTP)
    """
    status_code: int
    message: str
    url: str
    details: Optional[Mapping[str, Any]] = None

    def __str__(self) -> str:
        base = f"ApiError(status={self.status_code}, url={self.url}, message={self.message})"
        return base if not self.details else f"{base} details={dict(self.details)}"


class RateLimitError(ConnectorError):
    """Erreur de limite (429, quota, throttling)."""
