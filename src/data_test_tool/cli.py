from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .engine.runner import TestRunner


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run data testing definitions and generate reports.")
    parser.add_argument("--test", required=True, help="Path to a YAML test definition file.")
    parser.add_argument("--output", default="reports", help="Output directory for generated reports.")
    args = parser.parse_args(argv)

    runner = TestRunner()
    results = runner.run(args.test)
    runner.write_reports(results, args.output)

    failed = [result for result in results if not result.passed]
    if failed:
        print(f"{len(failed)} checks failed. See reports in {Path(args.output).resolve()}")
        return 1

    print(f"All checks passed. Reports written to {Path(args.output).resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
