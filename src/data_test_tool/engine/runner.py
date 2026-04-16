from __future__ import annotations

import yaml
from pathlib import Path
from typing import Any

from ..engine.evaluator import RuleEvaluator, EvaluationResult
from ..models.test_definition import TestDefinition
from ..reporting.json_report import JsonReport
from ..reporting.junit_report import JunitReport


class TestRunner:
    def __init__(self):
        self.evaluator = RuleEvaluator()

    def load_test_definition(self, filepath: str) -> TestDefinition:
        path = Path(filepath)
        content = yaml.safe_load(path.read_text())
        return TestDefinition(**content["test"])

    def run(self, filepath: str) -> list[EvaluationResult]:
        test_definition = self.load_test_definition(filepath)
        return self.evaluator.evaluate(test_definition)

    def write_reports(self, results: list[EvaluationResult], output_dir: str) -> None:
        report_path = Path(output_dir)
        report_path.mkdir(parents=True, exist_ok=True)
        JsonReport.write(results, report_path / "results.json")
        JunitReport.write(results, report_path / "results.xml")
