from pathlib import Path

import pytest
from analyticq.util import AnalyticQConst
from analyticq.util.path_util import (
    create_folder_if_not_exists_async,
    get_backend_default_config_AnalyticQ_path,
    get_backend_default_test_AnalyticQ_path,
    get_codebase_repositories_folder_AnalyticQ_path,
    get_codebase_scripts_folder_AnalyticQ_path, get_config_AnalyticQ_path,
    get_current_cwd_path, get_default_AnalyticQ_config_filename,
    get_home_AnalyticQ_path, get_last_dir_name, get_os_home_path)


def test_get_default_AnalyticQ_config_filename():

    # Default case
    assert get_default_AnalyticQ_config_filename() == 'analyticq_backend_config.json'

    # Test with JSON extension
    assert get_default_AnalyticQ_config_filename(AnalyticQConst.JSON_EXTENSION) == 'analyticq_backend_config.json'

    # Test with YAML extension
    assert get_default_AnalyticQ_config_filename(AnalyticQConst.YAML_EXTENSION) == 'analyticq_backend_config.yaml'

    # Test with YML extension (fallback)
    assert get_default_AnalyticQ_config_filename(AnalyticQConst.YML_EXTENSION) == 'analyticq_backend_config.yml'

    # Test with an unsupported extension (should fallback to YML)
    assert get_default_AnalyticQ_config_filename('unsupported') == 'analyticq_backend_config.yml'


def test_get_last_dir_name():
    # Test with a file path
    file_path = Path("/home/user/file.txt")
    assert get_last_dir_name(file_path) == "file.txt", "Expected equality"

    # Test with a directory path
    dir_path = Path("/home/user/docs/")
    assert get_last_dir_name(dir_path) == "docs", "Expected equality"

    # Test with a directory at the end
    dir_path = Path("/home/user/docs")
    assert get_last_dir_name(dir_path) == "docs", "Expected equality"


def test_get_last_dir_with_multiple_dir():
    nested_path = Path("/home/user/docs/file.txt")
    assert get_last_dir_name(nested_path) == "file.txt", "Expected equality"


def test_get_last_dir_name_empty():
    with pytest.raises(ValueError):
        get_last_dir_name(Path())


def test_get_home_path():
    expected_path = Path.home()
    result = get_os_home_path()
    assert result == expected_path, f"Expected equality for {expected_path}, got {result}"


def test_get_home_AnalyticQ_path():
    # Assuming the home directory is mocked for testing
    expected_path = Path.home() / ".analyticq"
    assert get_home_AnalyticQ_path() == expected_path, f"Expected equality for {expected_path}"


def test_get_current_cwd_path():
    # Mocking the current working directory
    expected_path = Path.cwd()
    assert get_current_cwd_path() == expected_path, f"Expected equality for {expected_path}"


def test_get_config_AnalyticQ_path():
    mock_home_path = Path.home()
    expected_path = mock_home_path / AnalyticQConst.ANALYTICQ_BASE_DIR / AnalyticQConst.ANALYTICQ_CONFIG_FOLDER
    result = get_config_AnalyticQ_path()
    assert result == expected_path, f"Expected equality for {expected_path}"


def test_get_backend_default_config_AnalyticQ_path():
    mock_cwd_path = Path.cwd()
    expected_path = mock_cwd_path / AnalyticQConst.ANALYTICQ_CONFIG_FOLDER
    result = get_backend_default_config_AnalyticQ_path()
    assert result == expected_path, f"Expected equality for {expected_path}, got {result}"


def test_get_backend_default_test_AnalyticQ_path():
    mock_cwd_path = Path.cwd()
    expected_path = mock_cwd_path / AnalyticQConst.ANALYTICQ_TEST_FILE_FOLDER
    result = get_backend_default_test_AnalyticQ_path()
    assert result == expected_path, f"Expected equality for {expected_path}, got {result}"


def test_get_codebase_repositories_folder_AnalyticQ_path():
    mock_cwd_path = Path.home()
    expected_path = mock_cwd_path / AnalyticQConst.ANALYTICQ_BASE_DIR / AnalyticQConst.ANALYTICQ_REPOS_FOLDER
    result = get_codebase_repositories_folder_AnalyticQ_path()
    assert result == expected_path, f"Expected equality for {expected_path}, got {result}"


def test_get_codebase_scripts_folder_AnalyticQ_path():
    mock_cwd_path = Path.home()
    expected_path = mock_cwd_path / AnalyticQConst.ANALYTICQ_BASE_DIR / AnalyticQConst.ANALYTICQ_SCRIPTS_FOLDER
    result = get_codebase_scripts_folder_AnalyticQ_path()
    assert result == expected_path, f"Expected equality for {expected_path}, got {result}"


@pytest.mark.asyncio
async def test_create_folder_if_not_exists_async_success(tmp_path):
    folder_path = tmp_path / "new_folder"
    # Simulate folder doesn't exist (initially it doesn't)
    result = await create_folder_if_not_exists_async(folder_path)

    assert result is True, f"Expected True for {folder_path}, got {result}"
    assert folder_path.exists()


@pytest.mark.asyncio
async def test_create_folder_if_not_exists_async_failure(tmp_path):
    folder_path = tmp_path / "existing_folder"
    folder_path.mkdir()

    result = await create_folder_if_not_exists_async(folder_path)
    assert result is False, f"Expected False for {folder_path}, got {result}"
