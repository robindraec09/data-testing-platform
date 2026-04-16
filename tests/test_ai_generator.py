from pathlib import Path

import pandas as pd

from data_test_tool.ai.generator import generate_rules_from_dataframe
from data_test_tool.ai.nlp import parse_nl_to_rules


def test_suggest_rules_from_dataframe() -> None:
    df = pd.DataFrame(
        {
            "customer_id": [1, 2, 3],
            "email": ["a@x.com", "b@x.com", "c@x.com"],
            "age": [34, 29, 41],
        }
    )
    rules = generate_rules_from_dataframe(df)
    assert any("not_null" in list(rule) for rule in rules)
    assert any("unique" in list(rule) for rule in rules)
    assert any("regex" in list(rule) for rule in rules)


def test_parse_nl_to_rules() -> None:
    rules = parse_nl_to_rules("Ensure no duplicate customer IDs and valid email addresses.")
    assert any("unique" in list(rule) for rule in rules)
    assert any("regex" in list(rule) for rule in rules)
