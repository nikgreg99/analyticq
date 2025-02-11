from typing import Dict
from unittest.mock import Mock

import pytest
from analyticq.preprocessing import (CodebaseMetricsCalculator,
                                     CodebaseMetricsCollector,
                                     CodebaseMetricsReporter)
from dependency_injector import containers, providers


class TestContainer(containers.DeclarativeContainer):
    metric_collector = providers.Singleton(Mock(spec=CodebaseMetricsCollector))
    metric_calculator = providers.Singleton(Mock(spec=CodebaseMetricsCalculator))


@pytest.fixture
def container():
    """Fixture for dependency injection container."""
    container = TestContainer()
    container.wire(modules=[__name__])
    return container


@pytest.fixture
def mock_collected_data() -> Dict:
    """Fixture for mock collected data."""
    return {
        "language_stats": {
            "Python": {
                "count": 10,
                "total_size": 5000,
                "files": [
                    {"file_path": "test.py", "loc": 100},
                    {"file_path": "main.py", "loc": 200}
                ],
                "largest_file": {"path": "main.py", "size": 3000},
                "smallest_file": {"path": "test.py", "size": 2000}
            }
        },
        "total_files": 10,
        "total_size": 5000,
        "excluded_dirs": [".git", "venv"],
        "excluded_files": {
            "count": 2,
            "total_size": 1000,
            "files": ["excluded1.py", "excluded2.py"]
        }
    }


@pytest.fixture
def mock_computed_metrics() -> Dict:
    """Fixture for mock computed metrics."""
    return {
        "Python": {
            "file_count": 10,
            "percentage": 100.0,
            "total_size": 5000,
            "average_size": 500,
            "largest_file": {"path": "main.py", "size": 3000},
            "smallest_file": {"path": "test.py", "size": 2000}
        }
    }


@pytest.fixture
def reporter(container) -> CodebaseMetricsReporter:
    return CodebaseMetricsReporter(
        metric_collector=container.metric_collector(),
        metric_calculator=container.metric_calculator()
    )


def test_reporter_init(container, reporter):
    assert reporter.metric_collector is not None, "Expected metric_collector to be injected"
    assert reporter.metric_calculator is not None, "Expected metric_calculator to be injected"
    assert isinstance(reporter.metric_collector, Mock), "Expected metric_collector to be a mock"
    assert isinstance(reporter.metric_calculator, Mock), "Expcected metric_calculkator to be a mock"


def test_get_codebase_metric_report(container, reporter, mock_collected_data, mock_computed_metrics):
    # Setup mock returns
    reporter.metric_collector.get_collected_data.return_value = mock_collected_data
    reporter.metric_calculator.compute_language_metrics.return_value = mock_computed_metrics

    report = reporter.get_codebase_metric_report()

    reporter.metric_collector.get_collected_data.assert_called_once(), "Expected get_collected_data to be called once"

    reporter.metric_calculator.compute_language_metrics.assert_called_once_with(
        mock_collected_data["language_stats"], mock_collected_data["total_files"]
    )

    # Verify report structure and content
    assert isinstance(report, dict), "Exptected report to be a dictionary"
    assert "language_statistics" in report, "Expected language_statistics in report"
    assert "total_files_scanned" in report, "Expected total_files_scanned in report"
    assert "total_size_scanned" in report, "Expected total_size_scanned in report"
    assert "excluded_directories" in report, "Expected excluded_directories in report"
    assert "excluded_files" in report, "Expected excluded_files in report"

    # Verify report outcome
    assert report["language_statistics"] == mock_computed_metrics, "Expected language statistics to match computed metrics"
    assert report["total_files_scanned"] == mock_collected_data["total_files"], "Expected total files to match collected data"
    assert report["total_size_scanned"] == mock_collected_data["total_size"], "Expected total size to match collected data"
    assert report["excluded_directories"] == mock_collected_data["excluded_dirs"], "Expected excluded directories to match collected data"
    assert report["excluded_files"] == mock_collected_data["excluded_files"], "Expected excluded files to match collected data"


def test_empty_report(container, reporter):
    """Test report generation with empty data."""
    empty_collected_data = {
        "language_stats": {},
        "total_files": 0,
        "total_size": 0,
        "excluded_dirs": [],
        "excluded_files": {
            "count": 0,
            "total_size": 0,
            "files": []
        }
    }
    empty_computed_metrics = {}

    reporter.metric_collector.get_collected_data.return_value = empty_collected_data
    reporter.metric_calculator.compute_language_metrics.return_value = empty_computed_metrics

    report = reporter.get_codebase_metric_report()

    assert report["total_files_scanned"] == 0, "Expected zero total files for empty report"
    assert report["total_size_scanned"] == 0, "Expected zero total size for empty report"
    assert len(report["excluded_directories"]) == 0, "Expected no excluded directories"
    assert report["excluded_files"]["count"] == 0, "Expected no excluded files"
