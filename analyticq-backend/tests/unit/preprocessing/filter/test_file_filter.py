from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from analyticq.preprocessing import FileFilter


@pytest.fixture(scope="function")
def mock_file_filter_conf():
    # Mock configuration for max file size and other settings
    mock_config = {
        "file_filter": {
            "extensions_excluded": [".exe", ".jpg"],
            "filenames_excluded": ["LICENSE", "README.md"],
            "max_file_size": 50 * 1024 * 1024  # 50 MB
        }
    }

    # Patch the get method to return the mock config
    with patch("analyticq.config.AnalyticQBaseConfig.get", return_value=mock_config):
        # Load the configuration to apply it to FileFilter
        FileFilter.load_file_filter_conf()
        yield mock_config  # Yield the config if needed in test cases


def test_is_hidden_file():

    with patch("analyticq.preprocessing.filter.file_filter.os") as mock_os_path:
        mock_stat = MagicMock()
        mock_stat.st_file_attributes = 2  # Hidden attribute (Windows)
        mock_os_path.stat.return_value = mock_stat

        hidden_file = Path("path/to/.hiddenfile")
        result = FileFilter.is_hidden_file(hidden_file)
        assert result is True, f"Expected true for hidden file, {result}"


def test_file_not_hidden_file():

    with patch("analyticq.preprocessing.filter.file_filter.os") as mock_os_path:
        mock_stat = MagicMock()
        mock_stat.st_file_attributes = 0  # Hidden attribute (Windows)
        mock_os_path.stat.return_value = mock_stat

        visible_file = Path("path/to/visible_file")
        result = FileFilter.is_hidden_file(visible_file)
        assert result is False, f"Expected false for visible file, {result}"


def test_is_empty_file():
    with patch.object(Path, "stat") as mock_stat:
        # Simulate empty file
        mock_stat.return_value.st_size = 0
        empty_file = Path("/path/to/empty_file.txt")
        result = FileFilter.is_empty_file(empty_file)
        assert result is True, f"Expected True for empty file, got {result}"


def test_is_not_empty_file():
    with patch.object(Path, "stat") as mock_stat:
        # Simulate empty file
        mock_stat.return_value.st_size = 5000
        empty_file = Path("/path/to/not_empty.txt")
        result = FileFilter.is_empty_file(empty_file)
        assert result is False, f"Expected False for non empty file, got {result}"


def test_is_binary_file():
    with patch("filetype.guess") as mock_guess:
        mock_guess.return_value = MagicMock()
        binary_file = Path("/path/to/binary.exe")
        result = FileFilter.is_binary_file(binary_file)
        assert result is True, f"Expected True for binary file, got {result}"


def test_is_not_binary_file():
    with patch("filetype.guess") as mock_guess:
        mock_guess.return_value = None
        non_binary_file = Path("/path/to/textfile.txt")
        result = FileFilter.is_binary_file(non_binary_file)
        assert result is False, f"Expected False for non binary file {non_binary_file}, got {result}"


def test_is_file_ok(mock_file_filter_conf):
    with patch.object(Path, "stat") as mock_stat:
        mock_stat.return_value.st_size = 10 * 1024 * 1024
        file = Path("/path/to/file.txt")

        result = FileFilter.is_file_size_ok(file)
        assert result is True, f"Expected True, for {file}  got {result}"


def test_is_file_size_not_ok(mock_file_filter_conf):
    with patch.object(Path, "stat") as mock_stat:
        mock_stat.return_value.st_size = 60 * 1024 * 1024
        large_file = Path("/path/to/largefile.txt")

        result = FileFilter.is_file_size_ok(large_file)
        assert result is False, f"Expected False for {large_file}, got {result}"


def test_file_size_is_ok_exaclty(mock_file_filter_conf):
    with patch.object(Path, "stat") as mock_stat:
        mock_stat.return_value.st_size = 50 * 1024 * 1024
        large_file = Path("/path/to/largefile.txt")

        result = FileFilter.is_file_size_ok(large_file)
        assert result is True, f"Expected True for {large_file}, got {result}"


def test_is_extension_excluded(mock_file_filter_conf):
    jpg_file = Path("/path/to/file.jpg")
    result = FileFilter.is_extension_excluded(jpg_file)
    assert result is True, f"Expected True for excluded extension, got {result}"


def test_is_extension_not_excluded(mock_file_filter_conf):
    java_file = Path("/path/to/Hello.java")
    result = FileFilter.is_extension_excluded(java_file)
    assert result is False, f"Expected False for excluded extension, got {result}"


def test_is_filename_excluded(mock_file_filter_conf):
    license_file = Path("/path/to/LICENSE")
    result = FileFilter.is_filename_excluded(license_file)
    assert result is True, f"Expected True for excluded filename {license_file}, got {result}"


def test_is_filename_not_excluded(mock_file_filter_conf):
    sample_file = Path("/path/to/sample.txt")
    result = FileFilter.is_filename_excluded(sample_file)
    assert result is False, f"Expected True for excluded filename {sample_file}, got {result}"


def test_is_file_relevant(mock_file_filter_conf):
    with patch("analyticq.preprocessing.filter.file_filter.FileFilter.is_empty_file") as mock_empty, \
         patch("analyticq.preprocessing.filter.file_filter.FileFilter.is_binary_file") as mock_binary, \
         patch("analyticq.preprocessing.filter.file_filter.FileFilter.is_file_size_ok") as mock_size_ok, \
         patch("analyticq.preprocessing.filter.file_filter.FileFilter.is_extension_excluded") as mock_extension, \
         patch("analyticq.preprocessing.filter.file_filter.FileFilter.is_filename_excluded") as mock_filename:
        # Simulate relevant file conditions
        mock_empty.return_value = False
        mock_binary.return_value = False
        mock_size_ok.return_value = True
        mock_extension.return_value = False
        mock_filename.return_value = False

        relevant_file = Path("/path/to/validfile.py")
        result = FileFilter.is_relevant_file(relevant_file)
        assert result is True, f"Expected True for relevant file {relevant_file}, got {result}"


def test_is_file_non_relevant(mock_file_filter_conf):
    with patch("analyticq.preprocessing.filter.file_filter.FileFilter.is_empty_file") as mock_empty, \
         patch("analyticq.preprocessing.filter.file_filter.FileFilter.is_binary_file") as mock_binary, \
         patch("analyticq.preprocessing.filter.file_filter.FileFilter.is_file_size_ok") as mock_size_ok, \
         patch("analyticq.preprocessing.filter.file_filter.FileFilter.is_extension_excluded") as mock_extension, \
         patch("analyticq.preprocessing.filter.file_filter.FileFilter.is_filename_excluded") as mock_filename:
        # Simulate relevant file conditions
        mock_empty.return_value = True
        mock_binary.return_value = False
        mock_size_ok.return_value = False
        mock_extension.return_value = False
        mock_filename.return_value = False

        irrelevant_file = Path("/path/to/emptyfile.txt")
        result = FileFilter.is_relevant_file(irrelevant_file)
        assert result is False, f"Expected False for irrelevant file {irrelevant_file}, got {result}"
