from pathlib import Path

from data_test_tool.engine.runner import TestRunner


def test_etl_runner_reads_example_yaml() -> None:
    test_file = Path("examples/etl_test.yaml")
    assert test_file.exists()

    runner = TestRunner()
    results = runner.run(str(test_file))

    assert any(result.passed for result in results)
    assert all(result.passed for result in results)
