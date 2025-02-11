from pathlib import Path
from unittest.mock import patch

import pytest
from analyticq.util import AnalyticQConst
from analyticq.util.path_util import PathUtil


def test_get_last_dir_name_from_file_and_dir_paths():
    # Test with a file path
    file_path = Path("/home/user/file.txt")
    assert PathUtil.get_last_dir_name(file_path) == "file.txt", "Expected equality"

    # Test with a directory path
    dir_path = Path("/home/user/docs/")
    assert PathUtil.get_last_dir_name(dir_path) == "docs", "Expected equality"

    # Test with a directory at the end
    dir_path = Path("/home/user/docs")
    assert PathUtil.get_last_dir_name(dir_path) == "docs", "Expected equality"


def test_get_last_dir_with_nested_paths():
    nested_path = Path("/home/user/docs/file.txt")
    assert PathUtil.get_last_dir_name(nested_path) == "file.txt", "Expected equality"


def test_get_last_dir_name_empty():
    with pytest.raises(ValueError):
        PathUtil.get_last_dir_name(Path())


def test_get_home_path():
    mock_home = Path("/mock/home")
    with patch("pathlib.Path.home", return_value=mock_home):
        result = PathUtil.get_os_home_path()
        assert result == mock_home, f"Expected equality for {mock_home}, got {result}"


def test_get_home_AnalyticQ_path():
    mock_home = Path("/mock/home")
    expected_path = mock_home / AnalyticQConst.ANALYTICQ_BASE_DIR
    # Assuming the home directory is mocked for testing
    with patch("pathlib.Path.home", return_value=mock_home):
        result = PathUtil.get_home_AnalyticQ_path()
        assert result == expected_path, f"Expected equality for {expected_path}"


def test_get_current_cwd_path():
    mock_cwd = Path("/mock/cwd")
    expected_path = mock_cwd
    # Mocking the current working directory
    with patch("pathlib.Path.cwd", return_value=mock_cwd):
        result = PathUtil.get_current_cwd_path()
        assert result == expected_path, f"Expected equality for {expected_path}"


def test_get_config_AnalyticQ_path():
    mock_home_path = Path("/mock/home")
    expected_path = mock_home_path / AnalyticQConst.ANALYTICQ_BASE_DIR / AnalyticQConst.ANALYTICQ_CONFIG_FOLDER
    with patch("pathlib.Path.home", return_value=mock_home_path):
        result = PathUtil.get_config_AnalyticQ_path()
        assert result == expected_path, f"Expected equality for {expected_path}"


def test_get_backend_default_config_AnalyticQ_path():
    mock_cwd_path = Path("/mock/cwd")
    expected_path = mock_cwd_path / AnalyticQConst.ANALYTICQ_CONFIG_FOLDER
    with patch("pathlib.Path.cwd", return_value=mock_cwd_path):
        result = PathUtil.get_backend_default_config_AnalyticQ_path()
        assert result == expected_path, f"Expected equality for {expected_path}, got {result}"


def test_get_backend_default_test_AnalyticQ_path():
    mock_cwd_path = Path.cwd()
    expected_path = mock_cwd_path / PathUtil.get_backend_default_test_AnalyticQ_path() / AnalyticQConst.ANALYTICQ_TEST_FILE_FOLDER
    with patch("pathlib.Path.cwd", return_value=mock_cwd_path):
        result = PathUtil.get_backend_default_test_file_AnalyticQ_path()
        assert result == expected_path, f"Expected equality for {expected_path}, got {result}"


def test_get_codebase_repositories_folder_AnalyticQ_path():
    mock_home_path = Path("/mock/home")
    expected_path = mock_home_path / AnalyticQConst.ANALYTICQ_BASE_DIR / AnalyticQConst.ANALYTICQ_REPOS_FOLDER
    with patch("pathlib.Path.home", return_value=mock_home_path):
        result = PathUtil.get_codebase_repositories_AnalyticQ_path()
        assert result == expected_path, f"Expected equality for {expected_path}, got {result}"


def test_get_codebase_scripts_folder_AnalyticQ_path():
    mock_home_path = Path("/mock/home")
    expected_path = mock_home_path / AnalyticQConst.ANALYTICQ_BASE_DIR / AnalyticQConst.ANALYTICQ_SCRIPTS_FOLDER
    with patch("pathlib.Path.home", return_value=mock_home_path):
        result = PathUtil.get_codebase_scripts_AnalyticQ_path()
        assert result == expected_path, f"Expected equality for {expected_path}, got {result}"


def test_get_codebase_scripts_path_AnalyaticQ_str():
    mock_home_path = Path("/mock/home")
    expected_path = str(mock_home_path / AnalyticQConst.ANALYTICQ_BASE_DIR / AnalyticQConst.ANALYTICQ_SCRIPTS_FOLDER)
    with patch("pathlib.Path.home", return_value=mock_home_path):
        result = PathUtil.get_codebase_scripts_path_AnalyticQ_str()
        assert result == expected_path, f"Expected equality for {expected_path}, got {result}"


def test_get_coddebase_repository_AnalyticQ_str():
    mock_home_path = Path("/mock/home")
    expected_path = str(mock_home_path / AnalyticQConst.ANALYTICQ_BASE_DIR / AnalyticQConst.ANALYTICQ_REPOS_FOLDER)
    with patch("pathlib.Path.home", return_value=mock_home_path):
        result = PathUtil.get_codebase_repositories_path_AnalyticQ_str()
        assert result == expected_path, f"Expected equality for {expected_path}, got {result}"


@pytest.mark.asyncio
async def test_create_folder_if_not_exists_async_success(tmp_path):
    folder_path = tmp_path / "new_folder"
    # Simulate folder doesn't exist (initially it doesn't)
    result = await PathUtil.create_folder_if_not_exists_async(folder_path)
    assert result is True, f"Expected True for {folder_path}, got {result}"
    assert folder_path.exists()


@pytest.mark.asyncio
async def test_create_folder_if_not_exists_async_failure(tmp_path):
    folder_path = tmp_path / "existing_folder"
    folder_path.mkdir()

    result = await PathUtil.create_folder_if_not_exists_async(folder_path)
    assert result is False, f"Expected False for {folder_path}, got {result}"
