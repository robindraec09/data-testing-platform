from __future__ import annotations

from typing import Any

import requests

from .base import Connector


class ApiConnector(Connector):
    def fetch(self, source_config: dict) -> dict[str, Any]:
        method = source_config.get("method", "GET").upper()
        url = source_config["url"]
        headers = source_config.get("headers", {})
        params = source_config.get("params", {})
        body = source_config.get("body")

        response = requests.request(method, url, headers=headers, params=params, json=body, timeout=source_config.get("timeout", 30))
        response.raise_for_status()
        try:
            body = response.json()
        except ValueError:
            body = {"text": response.text}
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": body,
        }

    def fetch_schema(self, source_config: dict) -> dict:
        raise NotImplementedError("API schema introspection is not supported by default")
