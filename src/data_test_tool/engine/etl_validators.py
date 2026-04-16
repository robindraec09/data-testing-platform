from __future__ import annotations

from typing import Any

import pandas as pd


def validate_incremental_load(source_df: pd.DataFrame, target_df: pd.DataFrame, key_column: str, timestamp_column: str) -> dict[str, Any]:
    """Validate incremental load by checking for new/updated records based on timestamp."""
    if key_column not in source_df.columns or key_column not in target_df.columns:
        return {"passed": False, "message": f"Key column {key_column} missing in source or target"}

    if timestamp_column not in source_df.columns or timestamp_column not in target_df.columns:
        return {"passed": False, "message": f"Timestamp column {timestamp_column} missing in source or target"}

    source_max_ts = source_df[timestamp_column].max()
    target_max_ts = target_df[timestamp_column].max()

    if source_max_ts <= target_max_ts:
        return {"passed": True, "message": "No new data to load"}

    new_records = source_df[source_df[timestamp_column] > target_max_ts]
    updated_records = source_df[source_df[timestamp_column] == source_max_ts]

    return {
        "passed": True,
        "message": f"Incremental load valid: {len(new_records)} new, {len(updated_records)} updated",
        "new_records": len(new_records),
        "updated_records": len(updated_records),
    }


def validate_scd_type2(source_df: pd.DataFrame, target_df: pd.DataFrame, key_column: str, effective_date_column: str, end_date_column: str) -> dict[str, Any]:
    """Basic SCD Type 2 validation: check for active records and history."""
    active_source = source_df[source_df[end_date_column].isna()]
    active_target = target_df[target_df[end_date_column].isna()]

    source_keys = set(active_source[key_column])
    target_keys = set(active_target[key_column])

    if source_keys == target_keys:
        return {"passed": True, "message": "SCD Type 2 active records match"}
    else:
        missing = source_keys - target_keys
        extra = target_keys - source_keys
        return {
            "passed": False,
            "message": f"SCD Type 2 mismatch: missing {len(missing)}, extra {len(extra)}",
            "missing_keys": list(missing),
            "extra_keys": list(extra),
        }
