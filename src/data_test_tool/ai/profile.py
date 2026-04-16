from __future__ import annotations

from typing import Any

import pandas as pd


def profile_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    return {
        "row_count": len(df),
        "columns": list(df.columns),
        "null_counts": df.isna().sum().to_dict(),
        "unique_counts": df.nunique(dropna=False).to_dict(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
    }


def suggest_rules_from_dataframe(df: pd.DataFrame) -> list[dict[str, Any]]:
    rules: list[dict[str, Any]] = []

    for column in df.columns:
        if df[column].isna().sum() == 0:
            rules.append({"not_null": {"column": column}})

        if df[column].nunique(dropna=False) == len(df):
            rules.append({"unique": {"column": column}})

        if df[column].dtype == "int64" or df[column].dtype == "float64":
            minimum = int(df[column].min(skipna=True))
            maximum = int(df[column].max(skipna=True))
            rules.append(
                {
                    "range": {
                        "column": column,
                        "min": minimum,
                        "max": maximum,
                    }
                }
            )

    for column in df.select_dtypes(include="object"):
        sample_values = df[column].dropna().astype(str).head(10).tolist()
        if any("@" in value for value in sample_values):
            rules.append(
                {
                    "regex": {
                        "column": column,
                        "pattern": "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+$",
                    }
                }
            )
            break

    return rules
