# src/optimation_core/api_client.py

from __future__ import annotations

import time
import logging
from typing import Any, Mapping, Optional

import requests

from .exceptions import ApiError, RateLimitError


class ApiClient:
    """
    Client REST standard Optimation (timeouts + erreurs + logging).
    Retry: tu peux l'ajouter plus tard. Commence simple.
    """

    def __init__(
        self,
        base_url: str,
        *,
        headers: Optional[Mapping[str, str]] = None,
        timeout_s: float = 15.0,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s
        self.log = logger or logging.getLogger("optimation.http")

        self.session = requests.Session()
        if headers:
            self.session.headers.update(dict(headers))

    def _url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = self._url(path)
        timeout = kwargs.pop("timeout", self.timeout_s)

        t0 = time.perf_counter()
        try:
            resp = self.session.request(method, url, timeout=timeout, **kwargs)
        except requests.RequestException as e:
            raise ApiError(status_code=0, message=str(e), url=url) from e
        finally:
            dt_ms = (time.perf_counter() - t0) * 1000

        self.log.info("%s %s -> %s (%.0fms)", method.upper(), url, resp.status_code, dt_ms)

        if resp.status_code == 429:
            raise RateLimitError(f"Rate limit (429) on {url}")

        if not (200 <= resp.status_code < 300):
            msg = ""
            try:
                payload = resp.json()
                msg = payload.get("error") or payload.get("message") or str(payload)
            except Exception:
                msg = resp.text.strip()
            raise ApiError(status_code=resp.status_code, message=msg[:1000], url=resp.url)

        # Parse JSON si possible, sinon texte
        ctype = (resp.headers.get("Content-Type") or "").lower()
        if resp.status_code == 204:
            return None
        if "application/json" in ctype:
            return resp.json()
        return resp.text

    def get(self, path: str, *, params: Optional[Mapping[str, Any]] = None, **kw: Any) -> Any:
        return self.request("GET", path, params=params, **kw)

    def post(self, path: str, *, json: Any = None, data: Any = None, **kw: Any) -> Any:
        return self.request("POST", path, json=json, data=data, **kw)
