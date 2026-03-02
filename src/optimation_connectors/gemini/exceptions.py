from dataclasses import dataclass
from typing import Any, Mapping, Optional

from optimation_core.exceptions import ConnectorError


@dataclass(frozen=True)
class ResourceExhausted(ConnectorError):
    status_code: int
    message: str
    details: Optional[Mapping[str, Any]] = None
