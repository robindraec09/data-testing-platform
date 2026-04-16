from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

class Connector(ABC):
    """Base connector interface for all supported sources."""

    @abstractmethod
    def fetch(self, source_config: dict) -> Any:
        raise NotImplementedError

    @abstractmethod
    def fetch_schema(self, source_config: dict) -> dict:
        raise NotImplementedError

    def execute_query(self, source_config: dict, query: str) -> Any:
        raise NotImplementedError("This connector does not support direct query execution")
