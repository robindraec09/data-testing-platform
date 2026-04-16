from __future__ import annotations

from typing import Any


def parse_nl_to_rules(prompt: str) -> list[dict[str, Any]]:
    normalized = prompt.lower()
    rules: list[dict[str, Any]] = []

    if "not null" in normalized or "required" in normalized:
        rules.append({"not_null": {"column": "id"}})

    if "duplicate" in normalized or "unique" in normalized:
        rules.append({"unique": {"column": "id"}})

    if "email" in normalized:
        rules.append(
            {
                "regex": {
                    "column": "email",
                    "pattern": "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+$",
                }
            }
        )

    if "age" in normalized or "range" in normalized:
        rules.append({"range": {"column": "age", "min": 0, "max": 120}})

    return rules
