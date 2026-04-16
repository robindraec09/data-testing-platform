from __future__ import annotations

from typing import Any

import pandas as pd

from .nlp import parse_nl_to_rules
from .profile import profile_dataframe, suggest_rules_from_dataframe
from ..models.test_definition import SourceConfig


def generate_rules_from_dataframe(df: pd.DataFrame) -> list[dict[str, Any]]:
    return suggest_rules_from_dataframe(df)


def generate_test_definition_from_dataframe(name: str, source: SourceConfig, df: pd.DataFrame) -> dict[str, Any]:
    return {
        "test": {
            "name": name,
            "type": "data_quality",
            "source": source.model_dump(),
            "rules": generate_rules_from_dataframe(df),
        }
    }


def generate_rules_from_text(prompt: str) -> list[dict[str, Any]]:
    return parse_nl_to_rules(prompt)


def generate_schema_suggestions(schema: dict[str, Any]) -> list[dict[str, Any]]:
    suggestions: list[dict[str, Any]] = []
    for field, field_meta in schema.items():
        if field_meta.get("type") == "string" and field.lower().endswith("email"):
            suggestions.append(
                {
                    "regex": {
                        "column": field,
                        "pattern": "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+$",
                    }
                }
            )
    return suggestions
