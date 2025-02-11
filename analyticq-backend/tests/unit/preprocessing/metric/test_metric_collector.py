from collections import defaultdict
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from analyticq.preprocessing import CodebaseMetricsCollector, FileMetrics
from analyticq.util import PathUtil


@pytest.fixture
def metric_collector():
    return CodebaseMetricsCollector()


@pytest.fixture
def mock_python_file():
    mock_path = MagicMock(spec=Path)
    mock_path.exists.return_value = True
    mock_path.__str__.return_value = "C:/test/file.py"
    mock_path.__fspath__.return_value = "C:/test/file.py"
    mock_stat = MagicMock()
    mock_stat.st_size = 100
    mock_path.stat.return_value = mock_stat
    return mock_path


@pytest.fixture
def mock_js_file():
    mock_path = MagicMock(spec=Path)
    mock_path.exists.return_value = True
    mock_path.__str__.return_value = "C:/test/file.js"
    mock_path.__fspath__.return_value = "C:/test/file.js"
    mock_stat = MagicMock()
    mock_stat.st_size = 50
    mock_path.stat.return_value = mock_stat
    return mock_path


@pytest.fixture
def python_file_metrics():
    return FileMetrics(
        path="C:/test/file.py",
        size=100,
        loc=10
    )


@pytest.fixture
def js_file_metrics():
    return FileMetrics(
        path="C:/test/file.js",
        size=50,
        loc=5
    )


def test_initial_state(metric_collector):
    """Test the initial state of the collector."""
    assert metric_collector.total_files == 0, "Expected initial total files count to be 0"
    assert metric_collector.total_size == 0, "Expected initial total size to be 0"
    assert metric_collector.excluded_file_count == 0, "Expected initial excluded file count to be 0"
    assert metric_collector.excluded_file_size == 0, "Expected initial excluded file size to be 0"
    assert isinstance(metric_collector.language_stats, defaultdict), "Expected language_stats to be a defaultdict"
    assert len(metric_collector.language_stats) == 0, "Expected language_stats to be empty initially"


def test_add_file_statistics_single(metric_collector, mock_python_file, python_file_metrics):
    """Test adding statistics for a single file."""
    metric_collector.add_file_statistics(
        mock_python_file,
        "Python",
        python_file_metrics.size,
        python_file_metrics.loc
    )

    python_stats = metric_collector.language_stats["Python"]

    assert python_stats["count"] == 1, "Expected exactly one Python file"
    assert python_stats["total_size"] == python_file_metrics.size, f"Expected total size to be {python_file_metrics.size}"
    assert python_stats["files"][0]["file_path"] == python_file_metrics.path, f"Expected file path to be {python_file_metrics.path}"
    assert python_stats["files"][0]["loc"] == python_file_metrics.loc, f"Expected LOC to be {python_file_metrics.loc}"

    assert python_stats["largest_file"] == {
        "path": python_file_metrics.path,
        "size": python_file_metrics.size
    }, "Expected largest file to match the only file added"

    assert python_stats["smallest_file"] == {
        "path": python_file_metrics.path,
        "size": python_file_metrics.size
    }, "Expected smallest file to match the only file added"

    assert metric_collector.total_files == 1, "Expected total files count to be 1"
    assert metric_collector.total_size == python_file_metrics.size, f"Expected total size to be {python_file_metrics.size}"


def test_add_file_statistics_multiple(metric_collector, mock_python_file, mock_js_file, python_file_metrics, js_file_metrics):
    """Test adding statistics for multiple files."""
    # Add Python file
    metric_collector.add_file_statistics(
        mock_python_file,
        "Python",
        python_file_metrics.size,
        python_file_metrics.loc
    )

    # Add JavaScript file
    metric_collector.add_file_statistics(
        mock_js_file,
        "JavaScript",
        js_file_metrics.size,
        js_file_metrics.loc
    )

    # Check Python stats
    python_stats = metric_collector.language_stats["Python"]
    assert python_stats["count"] == 1, "Expected exactly one Python file"
    assert python_stats["total_size"] == python_file_metrics.size, f"Expected Python total size to be {python_file_metrics.size}"
    assert python_stats["largest_file"] == {
        "path": python_file_metrics.path,
        "size": python_file_metrics.size
    }, "Expected Python largest file to match the added file"

    # Check JavaScript stats
    js_stats = metric_collector.language_stats["JavaScript"]
    assert js_stats["count"] == 1, "Expected exactly one JavaScript file"
    assert js_stats["total_size"] == js_file_metrics.size, f"Expected JavaScript total size to be {js_file_metrics.size}"
    assert js_stats["largest_file"] == {
        "path": js_file_metrics.path,
        "size": js_file_metrics.size
    }, "Expected JavaScript largest file to match the added file"

    # Check totals
    expected_total_size = python_file_metrics.size + js_file_metrics.size
    assert metric_collector.total_files == 2, "Expected total files count to be 2"
    assert metric_collector.total_size == expected_total_size, f"Expected total size to be {expected_total_size}"


def test_add_excluded_file(metric_collector, mock_python_file):
    """Test adding an excluded file."""
    size = 1024
    metric_collector.add_excluded_file(mock_python_file, size)

    assert str(mock_python_file) in metric_collector.excluded_files, "Expected file to be in excluded files list"
    assert metric_collector.excluded_file_count == 1, "Expected excluded file count to be 1"
    assert metric_collector.excluded_file_size == size, f"Expected excluded file size to be {size}"


def test_add_excluded_dir(metric_collector):
    """Test adding an excluded directory."""
    mock_dir = MagicMock(spec=Path)
    mock_dir.is_dir.return_value = True
    mock_dir.__str__.return_value = "/home/.git"

    with patch.object(PathUtil, "path_to_str", return_value=str(mock_dir)):
        metric_collector.add_excluded_dir(mock_dir)

    assert str(mock_dir) in metric_collector.excluded_dirs, "Expected directory to be in excluded directories list"


def test_get_collected_data(metric_collector, mock_python_file, python_file_metrics):
    """Test getting collected data."""
    metric_collector.add_file_statistics(
        mock_python_file,
        "Python",
        python_file_metrics.size,
        python_file_metrics.loc
    )

    mock_dir = MagicMock(spec=Path)
    mock_dir.is_dir.return_value = True
    mock_dir.__str__.return_value = "/home/.git"

    with patch.object(PathUtil, "path_to_str", return_value=str(mock_dir)):
        metric_collector.add_excluded_dir(mock_dir)

    data = metric_collector.get_collected_data()

    assert isinstance(data, dict), "Expected data to be a dictionary"
    assert all(key in data for key in [
        "language_stats",
        "total_files",
        "total_size",
        "excluded_files",
        "excluded_dirs"
    ]), "Expected all required keys in collected data"

    assert data["total_files"] == 1, "Expected total files count to be 1"
    assert data["total_size"] == python_file_metrics.size, f"Expected total size to be {python_file_metrics.size}"
    assert "Python" in data["language_stats"], "Expected Python stats to be present"
    assert str(mock_dir) in data["excluded_dirs"], "Expected excluded directory to be present"


def test_file_not_found(metric_collector):
    """Test handling of non-existent files."""
    mock_missing_file = MagicMock(spec=Path)
    mock_missing_file.exists.return_value = False

    with pytest.raises(FileNotFoundError, match="File not found"):
        metric_collector.add_file_statistics(mock_missing_file, "Python")


def test_invalid_directory(metric_collector):
    """Test handling of invalid directories."""
    mock_invalid_dir = MagicMock(spec=Path)
    mock_invalid_dir.is_dir.return_value = False

    with pytest.raises(NotADirectoryError, match="Not a directory"):
        metric_collector.add_excluded_dir(mock_invalid_dir)
