from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from analyticq.preprocessing import CodebaseMetricsCollector
from analyticq.util import PathUtil


@pytest.fixture
def metric_collector():
    return CodebaseMetricsCollector()


@pytest.fixture
def mock_file():
    mock_path = MagicMock(spec=Path)
    mock_path.__str__.return_value = "C:/test/file.py"
    mock_path.__fspath__.return_value = "C:/test/file.py"
    mock_stat = MagicMock()
    mock_stat.st_size = 100
    mock_path.stat.return_value = mock_stat
    return mock_path


@pytest.fixture
def mock_file_2():
    mock_path = MagicMock(spec=Path)
    mock_path.__str__.return_value = "C:/test/file.js"
    mock_path.__fspath__.return_value = "C:/test/file.js"
    mock_stat = MagicMock()
    mock_stat.st_size = 50
    mock_path.stat.return_value = mock_stat
    return mock_path


def test_init_metric_collector(metric_collector: CodebaseMetricsCollector):
    assert metric_collector.total_files == 0, "Expected null"
    assert metric_collector.total_size == 0, "Expected null"
    assert metric_collector.excluded_file_count == 0, "Expected null"
    assert metric_collector.excluded_file_size == 0, "Exptected null"
    assert metric_collector.language_stats == {}, "Expected empty"


def test_add_excluded_file(metric_collector: CodebaseMetricsCollector):
    file_path = Path("/path/to/excluded/excluded_file.py")
    size = 1024

    metric_collector.add_excluded_file(file_path, size)

    assert metric_collector.excluded_files == [str(file_path)], f"Expected {file_path}"
    assert metric_collector.excluded_file_count == 1, "Expected 1 since we add only one file"
    assert metric_collector.excluded_file_size == size, f"Expected equal to {size}"


def test_add_excluded_dir(metric_collector: CodebaseMetricsCollector):
    dir_path = Path("/home/.git")

    with patch.object(PathUtil, "path_to_str", return_value=str(dir_path)):
        metric_collector.add_excluded_dir(dir_path)

    assert metric_collector.excluded_dirs == [str(dir_path)], f"Expected equals to {str(dir_path)}"


def test_add_single_file_statistics(metric_collector, mock_file):

    expected_Python_count = 1
    expected_Python_total_size = 100
    expected_Python_file = "C:/test/file.py"

    expected_total_files = 1
    expected_file_size = 100

    metric_collector.add_file_statistics(mock_file, "Python", 100, 10)

    assert metric_collector.language_stats["Python"]["count"] == expected_Python_count, f"Expected {expected_Python_count}"
    assert metric_collector.language_stats["Python"]["total_size"] == expected_Python_total_size, f"Expected {expected_Python_total_size}"
    assert metric_collector.language_stats["Python"]["files"][0]["file_path"] == "C:/test/file.py", f"Expected list with one filename {expected_Python_file}"
    assert metric_collector.total_files == expected_total_files, f"Expected {expected_total_files}"
    assert metric_collector.total_size == expected_file_size, f"Expected {expected_file_size}"


def test_add_multiple_file_statistics(metric_collector, mock_file, mock_file_2):

    expected_Python_count = 1
    expected_Python_total_file_size = 100
    expected_Python_file = "C:/test/file.py"

    expected_JS_count = 1
    expected_JS_total_filesize = 50
    expected_JS_file = "C:/test/file.js"

    expected_total_files = 2
    expected_file_size = 150

    metric_collector.add_file_statistics(mock_file, "Python", 100, 10)
    metric_collector.add_file_statistics(mock_file_2, "JS", 50, 10)

    assert metric_collector.language_stats["JS"]["count"] == expected_JS_count, f"Expected {expected_JS_count}"
    assert metric_collector.language_stats["Python"]["total_size"] == expected_Python_total_file_size, f"Expected {expected_Python_total_file_size}"
    assert metric_collector.language_stats["Python"]["files"][0]["file_path"] == expected_Python_file, f"Expected  {expected_Python_file}"

    assert metric_collector.language_stats["Python"]["count"] == expected_Python_count, f"Expected {expected_Python_count}"
    assert metric_collector.language_stats["JS"]["total_size"] == expected_JS_total_filesize, f"Expected {expected_JS_total_filesize}"
    assert metric_collector.language_stats["JS"]["files"][0]["file_path"] == expected_JS_file, f"Expected {expected_JS_file}"

    assert metric_collector.total_files == expected_total_files, f"Expected {expected_total_files}"
    assert metric_collector.total_size == expected_file_size, f"Expected {expected_file_size}"


def test_get_collected_data(metric_collector: CodebaseMetricsCollector):
    data = metric_collector.get_collected_data()

    assert "language_stats" in data
    assert "total_files" in data
    assert "total_size" in data
    assert "excluded_files" in data
    assert "excluded_dirs" in data
