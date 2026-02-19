from __future__ import annotations

from typing import Any, Optional

from optimation_core import ApiClient


class QueryApi:
    def __init__(self, http: ApiClient) -> None:
        self._http = http

    def list_class(self, class_name: str, query_params: dict | None = None) -> list[dict]:
        # Parse: GET /classes/<ClassName>
        data = self._http.get(f"/classes/{class_name}", params=query_params)
        # Parse retourne souvent {"results": [...]}
        if isinstance(data, dict) and "results" in data:
            return data["results"] or []
        return data if isinstance(data, list) else []

    def get_object(self, class_name: str, object_id: str) -> dict[str, Any]:
        # Parse: GET /classes/<ClassName>/<objectId>
        data = self._http.get(f"/classes/{class_name}/{object_id}")
        return data if isinstance(data, dict) else {"data": data}
    
    def update_object(self, class_name: str, object_id: str, json:dict):
        data = self._http.put(f'classes/{class_name}/{object_id}', json=json)
