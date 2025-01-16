import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from analyticq.exception import (CloneLocalRepositoryException,
                                 CloneLocalScriptException,
                                 CloneRemoteRepositoryException,
                                 CodebaseNotFoundException)
from analyticq.preprocessing import InputCloner, InputClonerProtocolType
from analyticq.utils import (get_codebase_repositories_folder_path,
                             get_codebase_scripts_folder_path, path_to_str)
from git.exc import GitCommandError


class MockCredentials:
    def __init__(self, auth_token: str):
        self.auth_token = auth_token


@pytest.fixture
def input_cloner():
    with patch('analyticq.config.AnalyticQBaseConfig.get') as mock_config:
        mock_config.return_value = {"default_branch": "main"}
        return InputCloner()


@pytest.mark.asyncio
async def test_clone_remote_codebase_succcess(input_cloner):

    codebase_url = "https://github.com/fake/repo.git"
    codebase_branch = "dev"
    repo_name = "repo"

    expected_repo_path = get_codebase_repositories_folder_path() / repo_name

    with patch('analyticq.utils.get_codebase_repositories_folder_path') , \
         patch("pathlib.Path.exists", return_value=False), \
         patch("git.Repo.clone_from") as mock_Repo:

        mock_repo_instance = MagicMock()
        mock_Repo.return_value = mock_repo_instance

        result_path = await input_cloner.clone_remote_codebase(codebase_url, codebase_branch)
        assert expected_repo_path == result_path
        mock_Repo.assert_called_once_with(codebase_url, expected_repo_path, branch=codebase_branch)


@pytest.mark.asyncio
async def test_clone_remote_codebase_with_default_branch(input_cloner):

    codebase_url = "https://github.com/fake/repo.git"
    repo_name = "repo"

    expected_repo_path = get_codebase_repositories_folder_path() / repo_name

    with patch('analyticq.utils.get_codebase_repositories_folder_path') , \
         patch("pathlib.Path.exists", return_value=False), \
         patch("git.Repo.clone_from") as mock_repo:

        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance

        result_path = await input_cloner.clone_remote_codebase(codebase_url)
        assert expected_repo_path == result_path
        mock_repo.assert_called_once_with(codebase_url, expected_repo_path, branch="main")


@pytest.mark.asyncio
async def test_clone_remote_codease_already_existing(input_cloner):

    codebase_url = "https://github.com/fake/repo.git"

    with patch('analyticq.utils.get_codebase_repositories_folder_path') , \
         patch("pathlib.Path.exists", return_value=True), \
         patch("git.Repo.clone_from") as mock_repo:

        mock_repo_instance = MagicMock()
        mock_repo.return_value = mock_repo_instance
        result_path = await input_cloner.clone_remote_codebase(codebase_url)
        assert result_path is None
        mock_repo.assert_not_called()


@pytest.mark.asyncio
async def test_clone_remote_codebase_failure(input_cloner):

    codebase_url = "https://github.com/fake/repo.git"

    with patch('analyticq.utils.get_codebase_repositories_folder_path') , \
         patch("pathlib.Path.exists", return_value=False), \
         patch("git.Repo.clone_from", side_effect=GitCommandError("Git Error")):

        with pytest.raises(CloneRemoteRepositoryException):
            await input_cloner.clone_remote_codebase(codebase_url)


@pytest.mark.asyncio
async def test_clone_remote_codebase_with_credentials(input_cloner):

    codebase_url = "https://github.com/fake/repo.git"
    branch = "dev"
    credentials = MockCredentials("fake_token")
    repo_name = "repo"

    expected_repo_path = get_codebase_repositories_folder_path() / repo_name

    with patch('analyticq.utils.get_codebase_repositories_folder_path', return_value=MagicMock()) , \
         patch("pathlib.Path.exists", return_value=False), \
         patch("git.Repo.clone_from") as mock_clone_from:

        repo_path = await input_cloner.clone_remote_codebase(codebase_url, branch, credentials)
        mock_clone_from.assert_called_once_with(
            f"https://{credentials.auth_token}@github.com/fake/repo.git",
            expected_repo_path,
            branch=branch
        )

        assert repo_path is not None


@pytest.mark.asyncio
async def test_clone_local_codebase_success(input_cloner):
    source_path = Path("/source/repo")
    dest_base_path = get_codebase_repositories_folder_path()

    with patch('analyticq.utils.get_codebase_repositories_folder_path') as mock_path, \
         patch('pathlib.Path.exists') as mock_exists, \
         patch('shutil.copytree') as mock_copy:

        mock_path.return_value = dest_base_path
        mock_exists.side_effect = [True, False]  # Source exists, destination doesn't

        await input_cloner.clone_local_codebase(path_to_str(source_path))

        mock_copy.assert_called_once_with(source_path, dest_base_path / "repo")


@pytest.mark.asyncio
async def test_clone_local_codebase_not_found(input_cloner):
    source_path = "/nonexisting/repo"
    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(CodebaseNotFoundException):
            await input_cloner.clone_local_codebase(source_path)


@pytest.mark.asyncio
async def test_clone_local_codebase_copy_failure(input_cloner):
    source_path = "/source/repo"
    dest_base_path = get_codebase_repositories_folder_path()
    with patch("analyticq.utils.get_codebase_repositories_folder_path") as mock_path, \
         patch("pathlib.Path.exists") as mock_exists, \
         patch("shutil.copytree", side_effect=shutil.Error('Simulate copy error')):

        mock_path.return_value = dest_base_path
        mock_exists.side_effect = [True, False]

        with pytest.raises(CloneLocalRepositoryException, match="Failed to copy codebase from"):
            await input_cloner.clone_local_codebase(source_path)


@pytest.mark.asyncio
async def test_clone_local_script_success(input_cloner):
    script_path = Path("/source/script.py")
    dest_path = get_codebase_scripts_folder_path()

    with patch('analyticq.utils.get_codebase_scripts_folder_path') as mock_path, \
         patch('pathlib.Path.exists') as mock_exists, \
         patch('shutil.copy') as mock_copy:

        # Return the actual path that the code is using
        mock_path.return_value = dest_path
        mock_exists.side_effect = [True, False]  # Source exists, destination doesn't

        await input_cloner.clone_local_script(script_path)
        # Assert with the exact path that's being used in the code
        mock_copy.assert_called_once_with(script_path, dest_path / "scripts")


@pytest.mark.asyncio
async def test_local_script_not_found(input_cloner):
    script_path = Path("/source/not_script.py")
    with patch("pathlib.Path.exists", return_value=False):
        with pytest.raises(CodebaseNotFoundException):
            await input_cloner.clone_local_script(script_path)


@pytest.mark.asyncio
async def test_clone_local_script_failure(input_cloner):
    script_path = Path("/source/script.py")
    dest_path = get_codebase_repositories_folder_path()

    with patch("analyticq.utils.get_codebase_repositories_folder_path") as mock_path, \
         patch("pathlib.Path.exists") as mock_exists, \
         patch("shutil.copy", side_effect=shutil.Error('Simulate copy error')):

        mock_path.return_value = dest_path
        mock_exists.side_effect = [True, False]
        with pytest.raises(CloneLocalScriptException):
            await input_cloner.clone_local_script(script_path)


def test_get_protocol(input_cloner):
    assert input_cloner._get_protocol("git@github.com:user/repo.git") == InputClonerProtocolType.SSH
    assert input_cloner._get_protocol("https://github.com/user/repo.git") == InputClonerProtocolType.HTTPS
    assert input_cloner._get_protocol("http://github.com/user/repo.git") == InputClonerProtocolType.HTTP
