from __future__ import annotations

import os

from optimation_core import ApiClient, ConfigError, get_logger
from .types import ParseCredential
from .query import QueryApi


class ParseClient:
    """
    ✅ Seul endroit où on lit/valide les creds (pas de répétition).
    Expose des sous-modules (query) comme ton pattern Service Aggregator.
    """

    def __init__(self, cred: ParseCredential | None = None) -> None:
        self.log = get_logger("optimation.connectors.parse")

        if cred is None:
            cred = self._from_env()

        self._validate(cred)

        headers = {
            "X-Parse-Application-Id": cred["app_id"],
            "X-Parse-Master-Key": cred["master_key"],
        }

        self.http = ApiClient(
            base_url=cred["base_url"].rstrip("/"),
            headers=headers,
            logger=self.log,
            timeout_s=15.0,
        )

        self.query = QueryApi(self.http)

    @staticmethod
    def _from_env() -> ParseCredential:
        return ParseCredential(
            base_url=os.getenv("PARSE_SERVER_URL", "") or "",
            app_id=os.getenv("PARSE_APP_ID", "") or "",
            master_key=os.getenv("PARSE_MASTER_KEY", "") or "",
        )

    @staticmethod
    def _validate(cred: ParseCredential) -> None:
        missing = [k for k, v in cred.items() if not v]
        if missing:
            raise ConfigError(f"Missing Parse credentials: {', '.join(missing)}")

