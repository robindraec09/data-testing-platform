from __future__ import annotations

import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional, Union
from .ml_anomaly_detector import MLAnomalyDetector


class AnomalyDetector:
    """Unified anomaly detection combining statistical and ML approaches."""

    def __init__(self, contamination: float = 0.1, random_state: int = 42):
        self.ml_detector = MLAnomalyDetector(contamination=contamination, random_state=random_state)
        self.baselines: Dict[str, Dict[str, Any]] = {}

    def establish_baseline(self, df: pd.DataFrame, column: str, method: str = "auto") -> None:
        """Establish baseline for anomaly detection.

        Args:
            df: DataFrame containing the data
            column: Column name to establish baseline for
            method: Detection method ('statistical', 'isolation_forest', 'dbscan', 'auto')
        """
        if method == "auto":
            # Choose method based on data characteristics
            series = pd.to_numeric(df[column], errors="coerce").dropna()
            if len(series) >= 100:
                method = "isolation_forest"  # Use ML for larger datasets
            else:
                method = "statistical"  # Use statistical for smaller datasets

        if method in ["isolation_forest", "dbscan"]:
            self.ml_detector.establish_baseline(df, column, method)
        else:
            # Statistical baseline
            series = pd.to_numeric(df[column], errors="coerce").dropna()
            if len(series) > 0:
                self.baselines[column] = {
                    "mean": series.mean(),
                    "std": series.std(),
                    "min": series.min(),
                    "max": series.max(),
                    "q25": series.quantile(0.25),
                    "q75": series.quantile(0.75),
                    "iqr": series.quantile(0.75) - series.quantile(0.25),
                    "count": len(series),
                    "method": "statistical",
                }

    def detect_anomalies(self, df: pd.DataFrame, column: str, method: str = "auto") -> Dict[str, Any]:
        """Detect anomalies in a column using specified or auto-selected method.

        Args:
            df: DataFrame containing the data
            column: Column name to check for anomalies
            method: Detection method ('statistical', 'isolation_forest', 'dbscan', 'auto')

        Returns:
            Dictionary with detection results
        """
        if method == "auto":
            # Auto-select method based on available baselines
            if column in self.ml_detector.models:
                method = "ml"
            elif column in self.baselines:
                method = "statistical"
            else:
                return {
                    "passed": False,
                    "message": f"No baseline established for {column}",
                    "anomalies": [],
                    "anomaly_score": 0.0,
                }

        if method == "ml" or method in ["isolation_forest", "dbscan"]:
            return self.ml_detector.detect_anomalies_ml(df, column)
        elif method == "statistical":
            return self._detect_statistical_anomalies(df, column)
        else:
            return {
                "passed": False,
                "message": f"Unsupported detection method: {method}",
                "anomalies": [],
                "anomaly_score": 0.0,
            }

    def _detect_statistical_anomalies(self, df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """Detect anomalies using statistical methods (IQR, Z-score)."""
        if column not in self.baselines:
            return {
                "passed": False,
                "message": f"No statistical baseline established for {column}",
                "anomalies": [],
                "anomaly_score": 0.0,
            }

        if column not in df.columns:
            return {
                "passed": False,
                "message": f"Column {column} not found",
                "anomalies": [],
                "anomaly_score": 0.0,
            }

        baseline = self.baselines[column]
        series = pd.to_numeric(df[column], errors="coerce").dropna()

        if len(series) == 0:
            return {
                "passed": False,
                "message": f"No numeric data in {column}",
                "anomalies": [],
                "anomaly_score": 0.0,
            }

        # IQR-based outlier detection
        q25, q75 = baseline["q25"], baseline["q75"]
        iqr = baseline["iqr"]
        lower_bound = q25 - 1.5 * iqr
        upper_bound = q75 + 1.5 * iqr

        # Z-score based detection (3-sigma rule)
        mean, std = baseline["mean"], baseline["std"]
        z_scores = np.abs((series - mean) / std)
        z_score_anomalies = z_scores > 3

        # Combine IQR and Z-score anomalies
        iqr_anomalies = (series < lower_bound) | (series > upper_bound)
        combined_anomalies = iqr_anomalies | z_score_anomalies

        anomaly_count = combined_anomalies.sum()
        total_count = len(series)

        if anomaly_count > 0:
            anomaly_values = series[combined_anomalies].tolist()
            anomaly_score = anomaly_count / total_count

            return {
                "passed": False,
                "message": f"Statistical analysis detected {anomaly_count}/{total_count} anomalies in {column}: {anomaly_values[:5]}{'...' if len(anomaly_values) > 5 else ''}",
                "anomalies": anomaly_values,
                "anomaly_score": float(anomaly_score),
                "bounds": {
                    "iqr_lower": float(lower_bound),
                    "iqr_upper": float(upper_bound),
                    "z_score_threshold": 3.0,
                },
            }
        else:
            return {
                "passed": True,
                "message": f"No statistical anomalies detected in {column}",
                "anomalies": [],
                "anomaly_score": 0.0,
                "bounds": {
                    "iqr_lower": float(lower_bound),
                    "iqr_upper": float(upper_bound),
                    "z_score_threshold": 3.0,
                },
            }

    def detect_multivariate_anomalies(self, df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """Detect anomalies across multiple correlated columns."""
        return self.ml_detector.detect_multivariate_anomalies(df, columns)

    def detect_seasonal_anomalies(self, df: pd.DataFrame, column: str, time_column: str) -> Dict[str, Any]:
        """Detect seasonal/time-based anomalies."""
        return self.ml_detector.detect_seasonal_anomalies(df, column, time_column)

    def get_baseline_info(self, column: str) -> Optional[Dict[str, Any]]:
        """Get baseline information for a column."""
        if column in self.baselines:
            return self.baselines[column]
        elif column in self.ml_detector.baseline_stats:
            return self.ml_detector.baseline_stats[column]
        return None

    def list_baselines(self) -> List[str]:
        """List all columns with established baselines."""
        statistical_cols = list(self.baselines.keys())
        ml_cols = list(self.ml_detector.baseline_stats.keys())
        return list(set(statistical_cols + ml_cols))