import os
from pathlib import Path
from unittest.mock import patch

import pytest
from analyticq.preprocessing import DirFilter
from analyticq.util import PathUtil


@pytest.fixture(scope="function")
def mock_dir_filter_conf():
    # Mock configuration for max file size and other settings
    mock_config = {
        "dir_filter": {
            "excluded_dirs": [".git",],
            "max_depth": 5
        }
    }

    # Patch the get method to return the mock config
    with patch("analyticq.config.AnalyticQBaseConfig.get", return_value=mock_config):
        # Load the configuration to apply it to FileFilter
        DirFilter.load_dir_filter_conf()
        yield mock_config  # Yield the config if needed in test cases


@pytest.fixture
def tmp_dir(tmp_path):
    dir_path = tmp_path / "test_dir"
    dir_path.mkdir()
    return dir_path


def test_is_empty_dir(tmp_dir):
    result = DirFilter.is_empty_dir(tmp_dir)
    assert result is True, f"Expected True form empty dir, got {result} "


def test_is_non_empty_dir(tmp_dir):
    (tmp_dir / "file.txt").touch()
    result = DirFilter.is_empty_dir(tmp_dir)
    assert result is False, f"Expected False form empty dir, got{result} "


def test_is_max_depth(mock_dir_filter_conf):
    deep_path = Path("/a/b/c/d/e/f")
    result = DirFilter.is_max_depth(deep_path)
    assert result is True, f"Expected True for {deep_path}, got{result} "


def test_is_non_max_depth(mock_dir_filter_conf):
    shallow_path = Path("/a/b/c/d/e")
    result = DirFilter.is_max_depth(shallow_path)
    assert result is False, f"Expected False for {shallow_path}, got {result} "


def test_is_read_only_dir(tmp_path):
    read_only_dir = tmp_path / "readonly"
    read_only_dir.touch(0o400)
    result = DirFilter.is_read_only_dir(read_only_dir)
    assert result is True, f"Expected True for {read_only_dir}, got {result}"


def test_is_not_read_only_dir(tmp_path):
    dir_all_permissions = tmp_path / "general"
    dir_all_permissions.touch()
    result = DirFilter.is_read_only_dir(dir_all_permissions)
    assert result is False, f"Expected True for {dir_all_permissions}, got {result}"


def test_is_non_local_dir():
    path = Path("/mnt/external")
    with patch('os.path.ismount', return_value=True):
        result = DirFilter.is_non_local_dir(path)
        assert result is True, f"Expected True for local_dir {path}, got {result}"


def test_is_local_dir():
    path = Path("/home/user")
    with patch('os.path.ismount', return_value=False):
        result = DirFilter.is_non_local_dir(path)
        assert result is False, f"Expected False for local_dir {path}, got {result}"


def test_is_symlink(tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    symlink = tmp_path / "symlink"
    if os.name == "nt":
        os.system(f'mklink /J "{symlink}" "{target}"')
    else:
        symlink.symlink_to(target)
    result = symlink.exists()
    assert result is True, f"Expected True for symlink {symlink}, got {result}"


def test_is_not_symlink(tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    result = DirFilter.is_symlink(target)
    assert result is False, f"Expected False for symlink {target}, got {result}"


def test_is_relevant_dir_use_case(mock_dir_filter_conf, tmp_path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    assert DirFilter.is_relevant_dir(empty_dir) is True, "Expected False for an empty dir"

    excluded_dir = tmp_path / ".git"
    excluded_dir.mkdir()
    assert DirFilter.is_relevant_dir(excluded_dir) is True, f"Expected False for {PathUtil.path_to_str(excluded_dir)}"

    deep_dir = Path("/a/b/c/d/e/f")
    assert DirFilter.is_relevant_dir(deep_dir) is True, f"Expected False for {PathUtil.path_to_str(deep_dir)}"

    with patch("os.path.ismount", return_value=True):
        external_dir = Path("/mnt/external")
        assert DirFilter.is_relevant_dir(deep_dir) is True, f"Expected False for {PathUtil.path_to_str(external_dir)}"
