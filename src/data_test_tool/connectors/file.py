from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from .base import Connector


class FileConnector(Connector):
    def fetch(self, source_config: dict) -> pd.DataFrame:
        path = Path(source_config["path"])
        file_type = source_config.get("format", path.suffix.lstrip(".").lower())

        if file_type == "csv":
            return pd.read_csv(path)
        if file_type == "json":
            return pd.read_json(path)
        if file_type in {"parquet", "pq"}:
            return pd.read_parquet(path)
        raise ValueError(f"Unsupported file format: {file_type}")

    def fetch_schema(self, source_config: dict) -> dict:
        df = self.fetch(source_config)
        return {col: str(dtype) for col, dtype in df.dtypes.items()}
