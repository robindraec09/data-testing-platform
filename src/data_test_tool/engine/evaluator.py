from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import jsonschema
import pandas as pd
from pydantic import BaseModel, Field

from ..ai.anomaly_detector import AnomalyDetector
from ..connectors.api import ApiConnector
from ..connectors.database import DatabaseConnector
from ..connectors.file import FileConnector
from ..models.test_definition import TestDefinition


class EvaluationResult(BaseModel):
    test_name: str
    rule: dict[str, Any]
    passed: bool
    message: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class RuleEvaluator:
    def __init__(self):
        self.connectors = {
            "file": FileConnector(),
            "postgres": DatabaseConnector(),
            "mysql": DatabaseConnector(),
            "mssql": DatabaseConnector(),
            "oracle": DatabaseConnector(),
            "rest": ApiConnector(),
            "api": ApiConnector(),
        }
        self.anomaly_detector = AnomalyDetector()

    def evaluate(self, test: TestDefinition) -> list[EvaluationResult]:
        source_type = test.source.type.lower()
        connector = self.connectors.get(source_type)
        if connector is None:
            raise ValueError(f"Unsupported source type: {source_type}")

        if test.type == "data_quality":
            df = connector.fetch(test.source.model_dump())
            return self._evaluate_data_quality(test, df)
        if test.type == "api_contract":
            response = connector.fetch(test.source.model_dump())
            return self._evaluate_api_contract(test, response)
        if test.type in {"etl", "etl_pipeline", "pipeline"}:
            return self._evaluate_etl(test)
        if test.type == "sql_assertion":
            if source_type not in {"postgres", "mysql", "mssql", "oracle"}:
                raise ValueError("SQL assertion source must be a database")
            return self._evaluate_sql_assertions(test)
        if test.type == "anomaly_detection":
            df = connector.fetch(test.source.model_dump())
            return self._evaluate_anomaly_detection(test, df)

        raise ValueError(f"Unsupported test type: {test.type}")

    def _evaluate_data_quality(self, test: TestDefinition, df: pd.DataFrame) -> list[EvaluationResult]:
        results: list[EvaluationResult] = []
        for rule_dict in test.rules:
            try:
                rule_name, payload = next(iter(rule_dict.items()))
                rule_name = rule_name.lower()
                if rule_name == "not_null":
                    passed = payload["column"] not in df.columns or df[payload["column"]].notnull().all()
                    message = "All values are non-null" if passed else "Null values found"
                elif rule_name == "unique":
                    passed = payload["column"] not in df.columns or df[payload["column"]].is_unique
                    message = "Column values are unique" if passed else "Duplicates found"
                elif rule_name == "regex":
                    column = payload["column"]
                    pattern = re.compile(payload["pattern"])
                    passed = column in df.columns and df[column].astype(str).apply(lambda v: bool(pattern.match(v))).all()
                    message = "Regex validation passed" if passed else "Regex validation failed"
                elif rule_name == "range":
                    column = payload["column"]
                    min_value = payload.get("min")
                    max_value = payload.get("max")
                    if column not in df.columns:
                        passed = False
                    else:
                        values = pd.to_numeric(df[column], errors="coerce")
                        passed = values.notnull().all()
                        if passed and min_value is not None:
                            passed = (values >= min_value).all()
                        if passed and max_value is not None:
                            passed = (values <= max_value).all()
                    message = "Range validation passed" if passed else "Range validation failed"
                else:
                    passed = False
                    message = f"Unsupported data quality rule: {rule_name}"
            except Exception as exc:
                passed = False
                message = f"Error evaluating rule: {exc}"

            results.append(EvaluationResult(test_name=test.name, rule=rule_dict, passed=passed, message=message))
        return results

    def _evaluate_api_contract(self, test: TestDefinition, response: Any) -> list[EvaluationResult]:
        results: list[EvaluationResult] = []
        for rule_dict in test.rules:
            try:
                rule_name, payload = next(iter(rule_dict.items()))
                rule_name = rule_name.lower()
                if rule_name == "schema":
                    schema_path = Path(payload["file"])
                    schema = json.loads(schema_path.read_text())
                    if not isinstance(response, dict) or "body" not in response:
                        passed = False
                        message = "Invalid API response payload"
                    else:
                        jsonschema.validate(instance=response["body"], schema=schema)
                        passed = True
                        message = "Schema validation passed"
                elif rule_name == "response_code":
                    passed = isinstance(response, dict) and response.get("status_code") == payload["value"]
                    message = "Response code matched" if passed else "Response code mismatch"
                else:
                    passed = False
                    message = f"Unsupported API rule: {rule_name}"
            except Exception as exc:
                passed = False
                message = f"Error evaluating rule: {exc}"
            results.append(EvaluationResult(test_name=test.name, rule=rule_dict, passed=passed, message=message))
        return results

    def _evaluate_etl(self, test: TestDefinition) -> list[EvaluationResult]:
        results: list[EvaluationResult] = []
        source_df = self._fetch_dataframe(test.source)
        target_df = self._fetch_dataframe(test.target)

        for rule_dict in test.rules:
            try:
                rule_name, payload = next(iter(rule_dict.items()))
                rule_name = rule_name.lower()
                if rule_name == "row_count_match":
                    passed = len(source_df) == len(target_df)
                    message = f"Row count source={len(source_df)} target={len(target_df)}"
                elif rule_name == "checksum_match":
                    columns = payload.get("columns")
                    if columns is None:
                        columns = list(source_df.columns.intersection(target_df.columns))
                    source_hash = self._compute_checksum(source_df, columns)
                    target_hash = self._compute_checksum(target_df, columns)
                    passed = source_hash == target_hash
                    message = f"Checksum source={source_hash} target={target_hash}"
                elif rule_name == "columns_match":
                    source_columns = set(source_df.columns)
                    target_columns = set(target_df.columns)
                    passed = source_columns == target_columns
                    message = "Columns match" if passed else f"Source columns={source_columns} target columns={target_columns}"
                else:
                    passed = False
                    message = f"Unsupported ETL rule: {rule_name}"
            except Exception as exc:
                passed = False
                message = f"Error evaluating ETL rule: {exc}"
            results.append(EvaluationResult(test_name=test.name, rule=rule_dict, passed=passed, message=message))
        return results

    def _fetch_dataframe(self, source: Any) -> pd.DataFrame:
        source_type = source.type.lower()
        connector = self.connectors.get(source_type)
        if connector is None:
            raise ValueError(f"Unsupported ETL source type: {source_type}")
        df = connector.fetch(source.model_dump())
        if not isinstance(df, pd.DataFrame):
            raise ValueError("ETL sources must return a pandas DataFrame")
        return df

    def _compute_checksum(self, df: pd.DataFrame, columns: list[str]) -> str:
        subset = df[columns].astype(str).fillna("")
        records = subset.apply(lambda row: "|".join(row.values), axis=1).sort_values()
        return str(hash(tuple(records)))

    def _evaluate_sql_assertions(self, test: TestDefinition) -> list[EvaluationResult]:
        db_connector = self.connectors[test.source.type.lower()]
        results: list[EvaluationResult] = []
        for rule_dict in test.rules:
            try:
                sql = rule_dict.get("sql")
                if not sql:
                    results.append(EvaluationResult(test_name=test.name, rule=rule_dict, passed=False, message="Missing SQL assertion"))
                    continue
                query_result = db_connector.execute_query(test.source.model_dump(), sql)
                scalar_result = query_result.scalar() if hasattr(query_result, "scalar") else None
                passed = bool(scalar_result)
                message = "SQL assertion passed" if passed else "SQL assertion failed"
            except Exception as exc:
                passed = False
                message = f"Error executing SQL assertion: {exc}"
            results.append(EvaluationResult(test_name=test.name, rule=rule_dict, passed=passed, message=message))
        return results

    def _evaluate_anomaly_detection(self, test: TestDefinition, df: pd.DataFrame) -> list[EvaluationResult]:
        """Evaluate anomaly detection rules using ML and statistical methods."""
        results: list[EvaluationResult] = []

        for rule_dict in test.rules:
            details = {}  # Initialize details
            try:
                rule_name, payload = next(iter(rule_dict.items()))
                rule_name = rule_name.lower()

                if rule_name == "establish_baseline":
                    # Establish baseline for anomaly detection
                    column = payload.get("column")
                    method = payload.get("method", "auto")
                    if column:
                        self.anomaly_detector.establish_baseline(df, column, method)
                        passed = True
                        message = f"Baseline established for {column} using {method} method"
                    else:
                        passed = False
                        message = "Missing column for baseline establishment"

                elif rule_name == "detect_anomalies":
                    # Detect anomalies in a column
                    column = payload.get("column")
                    method = payload.get("method", "auto")
                    if column:
                        detection_result = self.anomaly_detector.detect_anomalies(df, column, method)
                        passed = detection_result["passed"]
                        message = detection_result["message"]
                        details = {
                            "anomalies": detection_result.get("anomalies", []),
                            "anomaly_score": detection_result.get("anomaly_score", 0.0),
                            "method": method,
                        }
                        if "bounds" in detection_result:
                            details["bounds"] = detection_result["bounds"]
                    else:
                        passed = False
                        message = "Missing column for anomaly detection"

                elif rule_name == "multivariate_anomalies":
                    # Detect multivariate anomalies
                    columns = payload.get("columns", [])
                    if columns:
                        detection_result = self.anomaly_detector.detect_multivariate_anomalies(df, columns)
                        passed = detection_result["passed"]
                        message = detection_result["message"]
                        details = {
                            "anomalies": detection_result.get("anomalies", []),
                            "anomaly_score": detection_result.get("anomaly_score", 0.0),
                            "affected_columns": detection_result.get("affected_columns", []),
                        }
                    else:
                        passed = False
                        message = "Missing columns for multivariate anomaly detection"

                elif rule_name == "seasonal_anomalies":
                    # Detect seasonal anomalies
                    column = payload.get("column")
                    time_column = payload.get("time_column")
                    if column and time_column:
                        detection_result = self.anomaly_detector.detect_seasonal_anomalies(df, column, time_column)
                        passed = detection_result["passed"]
                        message = detection_result["message"]
                        details = {
                            "anomalies": detection_result.get("anomalies", []),
                            "anomaly_score": detection_result.get("anomaly_score", 0.0),
                        }
                    else:
                        passed = False
                        message = "Missing column or time_column for seasonal anomaly detection"

                else:
                    passed = False
                    message = f"Unsupported anomaly detection rule: {rule_name}"

            except Exception as exc:
                passed = False
                message = f"Error evaluating anomaly detection rule: {exc}"

            results.append(EvaluationResult(
                test_name=test.name,
                rule=rule_dict,
                passed=passed,
                message=message,
                details=details
            ))

        return results
