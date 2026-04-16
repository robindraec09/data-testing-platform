from pathlib import Path

from data_test_tool.engine.runner import TestRunner


def test_runner_reads_example_yaml(tmp_path: Path) -> None:
    test_file = Path("examples/data_quality.yaml")
    assert test_file.exists()

    runner = TestRunner()
    results = runner.run(str(test_file))

    assert any(result.passed for result in results)
