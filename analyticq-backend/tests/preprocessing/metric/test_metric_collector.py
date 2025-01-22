from concurrent.futures import Future
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from analyticq.preprocessing import CodebaseMetricsCollector
from analyticq.util import PathUtil


@pytest.fixture
def metric_collector():
    return CodebaseMetricsCollector()


def test_init_metric_collector(metric_collector):
    assert metric_collector.total_files == 0, "Expected null"
    assert metric_collector.total_size == 0, "Expected null"
    assert metric_collector.excluded_file_count == 0, "Expected null"
    assert metric_collector.excluded_file_size == 0, "Exptected null"
    assert metric_collector.language_stats == {}, "Expected empty"


def test_add_excluded_file(metric_collector):
    file_path = Path("/path/to/excluded/excluded_file.py")
    size = 1024

    metric_collector.add_excluded_file(file_path, size)

    assert metric_collector.excluded_files == [str(file_path)], f"Expected {file_path}"
    assert metric_collector.excluded_file_count == 1, "Expected 1 since we add only one file"
    assert metric_collector.excluded_file_size == size, f"Expected equal to {size}"


def test_add_excluded_dir(metric_collector):
    dir_path = Path("/home/.git")

    with patch.object(PathUtil, "path_to_str", return_value=str(dir_path)):
        metric_collector.add_excluded_dir(dir_path)

    assert metric_collector.excluded_dirs == [str(dir_path)], f"Expected equat to {str(dir_path)}"


@patch("analyticq.preprocessing.metric.metric_collector.Path.stat")
def test_process_file(mock_stat, metric_collector):
    file_path = Path("/path/to/file.py")
    language = "Python"
    file_size = 2048

    mock_stat.return_value.st_size = file_size
    with patch.object(PathUtil, "path_to_str", return_value=str(file_path)):
        metric_collector._process_file(file_path, language)

    assert metric_collector.language_stats[language]["count"] == 1
    assert metric_collector.language_stats[language]["total_size"] == file_size
    assert metric_collector.language_stats[language]["files"] == [str(file_path)], "Expected equality"
    assert metric_collector.total_files == 1
    assert metric_collector.total_size == file_size


def test_batch_generator(metric_collector):
    files = [Path(f"(/path/to(file{i}.py))") for i in range(10)]
    batch_size = 3
    batches = list(metric_collector._batch_generator(files, batch_size))

    assert len(batches) == 4
    assert batches[-1] == files[9:]


@patch("analyticq.preprocessing.metric.metric_collector.ThreadPoolExecutor")
def test_add_files_parallel(mock_executor, metric_collector):
    files = [Path(f"/path/to/file{i}.py") for i in range(5)]
    language = "Python"

    # Create mock executor and futures
    mock_executor_instance = mock_executor.return_value.__enter__.return_value
    mock_futures = [MagicMock(spec=Future) for _ in range(5)]
    for future in mock_futures:
        future.result.return_value = None

    # Make submit return a new future each time
    mock_executor_instance.submit.side_effect = mock_futures

    # Mock as_completed to return our futures
    with patch('analyticq.preprocessing.metric.metric_collector.as_completed', return_value=mock_futures):
        metric_collector.add_files_parallel(files, language, batch_size=2, max_workers=2)

    # Verify interactions
    assert mock_executor.called
    assert mock_executor_instance.submit.call_count == len(files)
    assert all(future.result.called for future in mock_futures)


def test_get_collected_data(metric_collector):
    data = metric_collector.get_collected_data()

    assert "language_stats" in data
    assert "total_files" in data
    assert "total_size" in data
    assert "excluded_files" in data
    assert "excluded_dirs" in data
