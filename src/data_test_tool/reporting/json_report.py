from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from ..engine.evaluator import EvaluationResult


class JsonReport:
    @staticmethod
    def write(results: Iterable[EvaluationResult], path: Path) -> None:
        payload = [
            {
                "test_name": result.test_name,
                "rule": result.rule,
                "passed": result.passed,
                "message": result.message,
                "details": result.details,
            }
            for result in results
        ]
        path.write_text(json.dumps(payload, indent=2))
