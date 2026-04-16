from __future__ import annotations

from pathlib import Path
from typing import Iterable

from ..engine.evaluator import EvaluationResult


class HtmlReport:
    @staticmethod
    def write(results: Iterable[EvaluationResult], path: Path) -> None:
        rows = "\n".join(
            f"<tr><td>{result.test_name}</td><td>{result.rule}</td><td>{result.passed}</td><td>{result.message}</td></tr>"
            for result in results
        )
        html = f"""<html><body><table border=\"1\"><tr><th>Test</th><th>Rule</th><th>Passed</th><th>Message</th></tr>{rows}</table></body></html>"""
        path.write_text(html)
