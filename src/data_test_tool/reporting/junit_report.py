from __future__ import annotations

from pathlib import Path
from typing import Iterable

from ..engine.evaluator import EvaluationResult


class JunitReport:
    @staticmethod
    def write(results: Iterable[EvaluationResult], path: Path) -> None:
        entries = []
        for result in results:
            result_name = result.test_name.replace(" ", "_")
            status = "passed" if result.passed else "failed"
            message = result.message or ""
            entries.append(
                f"    <testcase classname=\"{result_name}\" name=\"{status}\">"
                + (f"<failure>{message}</failure>" if not result.passed else "")
                + "</testcase>"
            )

        xml = """<?xml version='1.0' encoding='UTF-8'?>\n<testsuite>\n"""
        xml += "\n".join(entries)
        xml += "\n</testsuite>\n"
        path.write_text(xml)
