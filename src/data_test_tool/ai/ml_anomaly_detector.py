from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from typing import Any, Dict, List, Optional


class MLAnomalyDetector:
    """Advanced ML-based anomaly detection using multiple algorithms."""

    def __init__(self, contamination: float = 0.1, random_state: int = 42):
        self.contamination = contamination
        self.random_state = random_state
        self.models: Dict[str, Any] = {}
        self.scalers: Dict[str, Any] = {}
        self.baseline_stats: Dict[str, Any] = {}

    def establish_baseline(self, df: pd.DataFrame, column: str, method: str = "isolation_forest") -> None:
        """Establish baseline using ML algorithms."""
        if column not in df.columns:
            return

        # Prepare data
        series = pd.to_numeric(df[column], errors="coerce").dropna()
        if len(series) < 10:  # Need minimum data for ML
            return

        # Scale the data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(series.values.reshape(-1, 1))

        # Train ML model based on method
        if method == "isolation_forest":
            model = IsolationForest(
                contamination=self.contamination,
                random_state=self.random_state,
                n_estimators=100
            )
            model.fit(scaled_data)
        elif method == "dbscan":
            # Use DBSCAN for density-based clustering
            model = DBSCAN(eps=0.5, min_samples=5)
            model.fit(scaled_data)
        else:
            raise ValueError(f"Unsupported ML method: {method}")

        # Store model and scaler
        self.models[column] = model
        self.scalers[column] = scaler

        # Store traditional stats as fallback
        self.baseline_stats[column] = {
            "mean": series.mean(),
            "std": series.std(),
            "min": series.min(),
            "max": series.max(),
            "count": len(series),
            "method": method,
        }

    def detect_anomalies_ml(self, df: pd.DataFrame, column: str) -> Dict[str, Any]:
        """Detect anomalies using trained ML models."""
        if column not in self.models or column not in self.scalers:
            return {
                "passed": False,
                "message": f"No ML baseline established for {column}",
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

        series = pd.to_numeric(df[column], errors="coerce").dropna()
        if len(series) == 0:
            return {
                "passed": False,
                "message": f"No numeric data in {column}",
                "anomalies": [],
                "anomaly_score": 0.0,
            }

        # Scale the data
        scaled_data = self.scalers[column].transform(series.values.reshape(-1, 1))

        # Get predictions from ML model
        model = self.models[column]
        if hasattr(model, 'predict'):  # Isolation Forest
            predictions = model.predict(scaled_data)
            anomaly_scores = model.score_samples(scaled_data)
            # Isolation Forest: -1 for anomalies, 1 for normal
            anomalies = predictions == -1
            anomaly_score = np.mean(anomaly_scores < -0.5)  # Threshold for anomaly scores
        elif hasattr(model, 'labels_'):  # DBSCAN
            # DBSCAN: -1 for noise (anomalies), cluster labels for normal points
            anomalies = np.array([True if label == -1 else False for label in model.labels_])
            anomaly_score = np.mean(anomalies)
        else:
            return {
                "passed": False,
                "message": "Unsupported ML model type",
                "anomalies": [],
                "anomaly_score": 0.0,
            }

        anomaly_count = np.sum(anomalies)
        total_count = len(series)

        if anomaly_count > 0:
            anomaly_values = series[anomalies].tolist()
            return {
                "passed": False,
                "message": f"ML detected {anomaly_count}/{total_count} anomalies in {column}: {anomaly_values[:5]}{'...' if len(anomaly_values) > 5 else ''}",
                "anomalies": anomaly_values,
                "anomaly_score": float(anomaly_score),
                "anomaly_indices": np.where(anomalies)[0].tolist(),
            }
        else:
            return {
                "passed": True,
                "message": f"No ML-detected anomalies in {column}",
                "anomalies": [],
                "anomaly_score": float(anomaly_score),
            }

    def detect_multivariate_anomalies(self, df: pd.DataFrame, columns: List[str]) -> Dict[str, Any]:
        """Detect anomalies across multiple correlated columns."""
        available_columns = [col for col in columns if col in df.columns]
        if len(available_columns) < 2:
            return {
                "passed": False,
                "message": "Need at least 2 columns for multivariate anomaly detection",
                "anomalies": [],
            }

        # Prepare multivariate data
        data = df[available_columns].copy()
        for col in available_columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

        data = data.dropna()
        if len(data) < 10:
            return {
                "passed": False,
                "message": "Insufficient data for multivariate anomaly detection",
                "anomalies": [],
            }

        # Scale the multivariate data
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(data.values)

        # Use Isolation Forest for multivariate anomalies
        model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=100
        )
        model.fit(scaled_data)

        # Get predictions
        predictions = model.predict(scaled_data)
        anomaly_scores = model.score_samples(scaled_data)
        anomalies = predictions == -1

        anomaly_count = np.sum(anomalies)

        if anomaly_count > 0:
            anomaly_indices = np.where(anomalies)[0]
            return {
                "passed": False,
                "message": f"Multivariate analysis detected {anomaly_count}/{len(data)} anomalies across {available_columns}",
                "anomalies": anomaly_indices.tolist(),
                "anomaly_score": float(np.mean(anomaly_scores < -0.5)),
                "affected_columns": available_columns,
            }
        else:
            return {
                "passed": True,
                "message": f"No multivariate anomalies detected across {available_columns}",
                "anomalies": [],
                "anomaly_score": 0.0,
                "affected_columns": available_columns,
            }

    def detect_seasonal_anomalies(self, df: pd.DataFrame, column: str, time_column: str) -> Dict[str, Any]:
        """Detect seasonal/time-based anomalies."""
        if column not in df.columns or time_column not in df.columns:
            return {
                "passed": False,
                "message": f"Column {column} or time column {time_column} not found",
                "anomalies": [],
            }

        try:
            # Convert time column to datetime
            df_copy = df.copy()
            df_copy[time_column] = pd.to_datetime(df_copy[time_column], errors="coerce")
            df_copy = df_copy.dropna(subset=[time_column, column])

            if len(df_copy) < 20:  # Need sufficient data for seasonal analysis
                return {
                    "passed": False,
                    "message": "Insufficient data for seasonal anomaly detection",
                    "anomalies": [],
                }

            # Sort by time
            df_copy = df_copy.sort_values(time_column)

            # Simple seasonal decomposition (rolling statistics)
            series = pd.to_numeric(df_copy[column], errors="coerce").dropna()

            # Calculate rolling mean and std
            rolling_mean = series.rolling(window=min(10, len(series)//3), center=True).mean()
            rolling_std = series.rolling(window=min(10, len(series)//3), center=True).std()

            # Detect anomalies as points outside 3-sigma from rolling mean
            deviations = np.abs(series - rolling_mean)
            anomalies = deviations > (3 * rolling_std)

            anomaly_count = anomalies.sum() if anomalies.sum() > 0 else 0

            if anomaly_count > 0:
                anomaly_values = series[anomalies].tolist()
                return {
                    "passed": False,
                    "message": f"Seasonal analysis detected {int(anomaly_count)} anomalies in {column}",
                    "anomalies": anomaly_values,
                    "anomaly_score": float(anomaly_count / len(series)),
                }
            else:
                return {
                    "passed": True,
                    "message": f"No seasonal anomalies detected in {column}",
                    "anomalies": [],
                    "anomaly_score": 0.0,
                }

        except Exception as exc:
            return {
                "passed": False,
                "message": f"Error in seasonal anomaly detection: {exc}",
                "anomalies": [],
            }
