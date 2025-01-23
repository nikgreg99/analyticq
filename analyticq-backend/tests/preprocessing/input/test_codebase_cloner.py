import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from analyticq.exception import (CloneLocalRepositoryException,
                                 CloneLocalScriptException,
                                 CloneRemoteRepositoryException,
                                 CodebaseNotFoundException)
from analyticq.preprocessing import CodebaseCloner, CodebaseClonerProtocolType
from analyticq.util import PathUtil
from git.exc import GitCommandError


class MockCredentials:
    def __init__(self, auth_token: str):
        self.auth_token = auth_token


@pytest.fixture
def codebase_cloner():
    with patch('analyticq.config.AnalyticQBaseConfig.get') as mock_config:
        mock_config.return_value = {"default_branch": "main"}
        return CodebaseCloner()


@pytest.mark.asyncio
async def test_clone_remote_codebase_succcess(codebase_cloner):

    codebase_url = "https://github.com/fake/repo.git"
    codebase_branch = "dev"
    repo_name = "repo"

    expected_repo_path = PathUtil.get_codebase_repositories_AnalyticQ_path() / repo_name

    with patch('analyticq.util.PathUtil') , \
         patch("pathlib.Path.exists", return_value=False), \
         patch("git.Repo.clone_from") as mock_repo:

        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance

        result_path = await codebase_cloner.clone_remote_codebase(codebase_url, codebase_branch)
        assert expected_repo_path == result_path
        mock_repo.assert_called_once_with(codebase_url, expected_repo_path, branch=codebase_branch)


@pytest.mark.asyncio
async def test_clone_remote_codebase_with_default_branch(codebase_cloner):

    codebase_url = "https://github.com/fake/repo.git"
    repo_name = "repo"

    expected_repo_path = PathUtil.get_codebase_repositories_AnalyticQ_path() / repo_name

    with patch('analyticq.util.PathUtil') , \
         patch("pathlib.Path.exists", return_value=False), \
         patch("git.Repo.clone_from") as mock_repo:

        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance

        result_path = await codebase_cloner.clone_remote_codebase(codebase_url)
        assert expected_repo_path == result_path
        mock_repo.assert_called_once_with(codebase_url, expected_repo_path, branch="main")


@pytest.mark.asyncio
async def test_clone_remote_codebase_with_tag(codebase_cloner):
    codebase_url = "https://github.com/fake/repo.git"
    repo_name = "repo"
    tag_name = "sample-tag"

    expected_repo_path = PathUtil.get_codebase_repositories_AnalyticQ_path() / repo_name

    with patch('analyticq.util.PathUtil') , \
         patch("pathlib.Path.exists", return_value=False), \
         patch("git.Repo.clone_from") as mock_repo:

        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance

        result_path = await codebase_cloner.clone_remote_codebase(codebase_url, branch=tag_name)
        assert expected_repo_path == result_path
        mock_repo.assert_called_once_with(codebase_url, expected_repo_path, branch=tag_name)


@pytest.mark.asyncio
async def test_clone_remote_codebase_already_existing(codebase_cloner):

    codebase_url = "https://github.com/fake/repo.git"

    with patch('analyticq.util.PathUtil') , \
         patch("pathlib.Path.exists", return_value=True), \
         patch("git.Repo.clone_from") as mock_repo:

        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance
        result_path = await codebase_cloner.clone_remote_codebase(codebase_url)
        assert result_path is None
        mock_repo.assert_not_called()


@pytest.mark.asyncio
async def test_clone_remote_codebase_failure(codebase_cloner):

    codebase_url = "https://github.com/fake/repo.git"

    with patch('analyticq.util.PathUtil') , \
         patch("pathlib.Path.exists", return_value=False), \
         patch("git.Repo.clone_from", side_effect=GitCommandError("Git Error")):

        with pytest.raises(CloneRemoteRepositoryException):
            await codebase_cloner.clone_remote_codebase(codebase_url)


@pytest.mark.asyncio
async def test_clone_remote_codebase_with_credentials(codebase_cloner):

    codebase_url = "https://github.com/fake/repo.git"
    branch = "dev"
    credentials = MockCredentials("fake_token")
    repo_name = "repo"

    expected_repo_path = PathUtil.get_codebase_repositories_AnalyticQ_path() / repo_name

    with patch('analyticq.util.PathUtil', return_value=MagicMock()) , \
         patch("pathlib.Path.exists", return_value=False), \
         patch("git.Repo.clone_from") as mock_clone_from:

        repo_path = await codebase_cloner.clone_remote_codebase(codebase_url, branch, credentials=credentials)
        mock_clone_from.assert_called_once_with(
            f"https://{credentials.auth_token}@github.com/fake/repo.git",
            expected_repo_path,
            branch=branch
        )

        assert repo_path is not None


@pytest.mark.asyncio
async def test_clone_local_codebase_success(codebase_cloner):
    source_path = Path("/source/repo")
    dest_base_path = PathUtil.get_codebase_repositories_AnalyticQ_path() / source_path.name

    with patch('analyticq.util.PathUtil') as mock_path, \
         patch('pathlib.Path.exists') as mock_exists, \
         patch('shutil.copytree') as mock_copy:

        mock_path.return_value = dest_base_path
        mock_exists.side_effect = [True, False]  # Source exists, destination doesn't

        await codebase_cloner.clone_local_codebase(PathUtil.path_to_str(source_path))

        mock_copy.assert_called_once_with(source_path, dest_base_path)


@pytest.mark.asyncio
async def test_clone_local_codebase_not_found(codebase_cloner):
    source_path = "/nonexisting/repo"
    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(CodebaseNotFoundException):
            await codebase_cloner.clone_local_codebase(source_path)


@pytest.mark.asyncio
async def test_clone_local_codebase_copy_failure(codebase_cloner):
    source_path = "/source/repo"
    dest_base_path = PathUtil.get_codebase_repositories_AnalyticQ_path()
    with patch("analyticq.util.PathUtil") as mock_path, \
         patch("pathlib.Path.exists") as mock_exists, \
         patch("shutil.copytree", side_effect=shutil.Error('Simulate copy error')):

        mock_path.return_value = dest_base_path
        mock_exists.side_effect = [True, False]

        with pytest.raises(CloneLocalRepositoryException, match="Failed to copy codebase from"):
            await codebase_cloner.clone_local_codebase(source_path)


@pytest.mark.asyncio
async def test_clone_local_script_success(codebase_cloner):
    script_path = Path("/source/script.py")
    dest_path = PathUtil.get_codebase_scripts_AnalyticQ_path() / script_path.name

    with patch('analyticq.util.PathUtil') as mock_path, \
         patch('pathlib.Path.exists') as mock_exists, \
         patch('shutil.copy') as mock_copy:

        # Return the actual path that the code is using
        mock_path.return_value = dest_path
        mock_exists.side_effect = [True, False]  # Source exists, destination doesn't

        await codebase_cloner.clone_local_script(script_path)
        # Assert with the exact path that's being used in the code
        mock_copy.assert_called_once_with(script_path, dest_path)


@pytest.mark.asyncio
async def test_local_script_not_found(codebase_cloner):
    script_path = Path("/source/not_script.py")
    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(CodebaseNotFoundException):
            await codebase_cloner.clone_local_script(script_path)


@pytest.mark.asyncio
async def test_clone_local_script_failure(codebase_cloner):
    script_path = Path("/source/script.py")
    dest_path = PathUtil.get_codebase_repositories_AnalyticQ_path()

    with patch("analyticq.util.PathUtil") as mock_path, \
         patch("pathlib.Path.exists") as mock_exists, \
         patch("shutil.copy", side_effect=shutil.Error('Simulate copy error')):

        mock_path.return_value = dest_path
        mock_exists.side_effect = [True, False]
        with pytest.raises(CloneLocalScriptException):
            await codebase_cloner.clone_local_script(script_path)


def test_get_protocol(codebase_cloner):
    assert codebase_cloner._get_protocol("git@github.com:user/repo.git") == CodebaseClonerProtocolType.SSH
    assert codebase_cloner._get_protocol("https://github.com/user/repo.git") == CodebaseClonerProtocolType.HTTPS
    assert codebase_cloner._get_protocol("http://github.com/user/repo.git") == CodebaseClonerProtocolType.HTTP
