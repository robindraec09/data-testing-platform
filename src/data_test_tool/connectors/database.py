from __future__ import annotations

from typing import Any

import pandas as pd

from .base import Connector


class DatabaseConnector(Connector):
    def _create_engine(self, connection_string: str):
        from sqlalchemy import create_engine

        return create_engine(connection_string)

    def _prepare_sql(self, raw_sql: str):
        from sqlalchemy import text

        return text(raw_sql)

    def fetch(self, source_config: dict) -> pd.DataFrame:
        engine = self._create_engine(source_config["connection"])
        query = source_config.get("query")
        table = source_config.get("table")

        if query is None and table is None:
            raise ValueError("Database source must specify table or query")

        sql = query or f"SELECT * FROM {table}"
        with engine.connect() as connection:
            return pd.read_sql_query(self._prepare_sql(sql), connection)

    def fetch_schema(self, source_config: dict) -> dict:
        engine = self._create_engine(source_config["connection"])
        table = source_config.get("table")
        if table is None:
            raise ValueError("Database schema fetch requires a table name")

        with engine.connect() as connection:
            result = connection.execute(self._prepare_sql(f"SELECT * FROM {table} LIMIT 0"))
            return {col: str(dtype) for col, dtype in zip(result.keys(), result.cursor.description)}

    def execute_query(self, source_config: dict, query: str) -> Any:
        engine = self._create_engine(source_config["connection"])
        with engine.connect() as connection:
            return connection.execute(self._prepare_sql(query))
