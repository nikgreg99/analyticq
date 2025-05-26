import logging
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from analyticq.exception import (CloneLocalRepositoryException,
                                 CloneLocalScriptException,
                                 CloneRemoteRepositoryException,
                                 CodebaseNotFoundException,
                                 CodebaseUnknownTypeException,
                                 ExtractArchiveException)
from analyticq.preprocessing import (ArchiveType, CodebaseCloner,
                                     CodebaseClonerPathType,
                                     CodebaseClonerProtocolType)
from analyticq.service import GitAuthService
from analyticq.util import PathUtil
from git.exc import GitCommandError

logger = logging.getLogger(__name__)


@pytest.fixture
def codebase_cloner():
    git_auth_service = GitAuthService()
    with patch('analyticq.config.AnalyticQBaseConfig.get') as mock_config:
        mock_config.return_value = {"default_branch": "main"}
        return CodebaseCloner(git_auth_service)


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
        assert expected_repo_path == result_path, f"Expected {expected_repo_path}, got {result_path}"
        mock_repo.assert_called_once_with(codebase_url, expected_repo_path, branch=codebase_branch)


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
        assert expected_repo_path == result_path, f"Expected {expected_repo_path}, got {result_path}"
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
        assert result_path is not None, f"Expected {result_path} not to be none"
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
    fake_auth_token = "fake_token"
    repo_name = "repo"

    expected_repo_path = PathUtil.get_codebase_repositories_AnalyticQ_path() / repo_name

    with patch('analyticq.util.PathUtil', return_value=MagicMock()) , \
         patch("pathlib.Path.exists", return_value=False), \
         patch("git.Repo.clone_from") as mock_clone_from:

        repo_path = await codebase_cloner.clone_remote_codebase(codebase_url, branch=branch, tag=None, ssh_auth_token=fake_auth_token, protocol=CodebaseClonerProtocolType.SSH)
        mock_clone_from.assert_called_once_with(
            f"https://{fake_auth_token}@github.com/fake/repo.git",
            expected_repo_path,
            branch=branch,
        )

        assert repo_path is not None, f"Expected {expected_repo_path} not to be None"


@pytest.mark.asyncio
async def test_clone_local_codebase_success(codebase_cloner):
    source_path = Path("/source/repo")
    dest_base_path = PathUtil.get_codebase_repositories_AnalyticQ_path() / source_path.name

    with patch('analyticq.util.PathUtil.get_codebase_repositories_AnalyticQ_path', return_value=dest_base_path.parent), \
         patch.object(Path, 'exists', side_effect=[True, False, False]), \
         patch('shutil.copytree') as mock_copy:

        # Call the method
        await codebase_cloner.clone_local_codebase(str(source_path))

        # Verify that shutil.copytree was called with the correct arguments
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
        mock_exists.side_effect = [True, False, False]

        with pytest.raises(CloneLocalRepositoryException):
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
        mock_exists.side_effect = [True, False, False]  # Source exists, destination doesn't, and additional check

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
        mock_exists.side_effect = [True, False, False]
        with pytest.raises(CloneLocalScriptException):
            await codebase_cloner.clone_local_script(script_path)


@pytest.mark.parametrize(
    ("path", "exists", "is_file", "is_dir", "has_git", "is_archive", "expected"),
    [
        # Case 1: Remote repo
        ("https://github.com/user/repo.git", False, False, False, False, False, CodebaseClonerPathType.REMOTE_REPO),
        ("git@github.com:user/repo.git", False, False, False, False, False, CodebaseClonerPathType.REMOTE_REPO),

        # Case 2: Simulating non existing path
        ("/non/existing/path", False, False, False, False, False, CodebaseClonerPathType.UNKNOWN),

        # Case 3: Local script detection
        ("/home/user/script.py", True, True, False, False, False, CodebaseClonerPathType.SCRIPT),

        # Case 4: Local repository (no .git folder)
        ("/home/user/project", True, False, True, False, False, CodebaseClonerPathType.LOCAL_REPO),

        # Case 5: Git Repository
        ("/home/user/git_poject", True, False, True, True, False, CodebaseClonerPathType.GIT_REPO),

        # Case 6: Archive codebase
        ("/home/user/project.zip", True, True, False, False, True, CodebaseClonerPathType.ARCHIVE),
        ("/home/user/project.tar.gz", True, True, False, False, True, CodebaseClonerPathType.ARCHIVE),

    ]
)
def test_get_codebase_type(path, exists, is_file, is_dir, has_git, is_archive, expected, codebase_cloner):

    with patch("os.path.exists", return_value=exists), \
         patch("os.path.isfile", return_value=is_file), \
         patch("os.path.isdir", return_value=is_dir), \
         patch("os.path.exists", side_effect=lambda p: has_git if p.endswith(".git") else exists), \
         patch.object(CodebaseCloner, "_is_archive", return_value=is_archive):

        result = codebase_cloner._get_codebase_type(path)
        assert result == expected, f"Failed with path {path}"


def test_get_protocol(codebase_cloner):
    assert codebase_cloner._get_protocol("git@github.com:user/repo.git") == CodebaseClonerProtocolType.SSH
    assert codebase_cloner._get_protocol("https://github.com/user/repo.git") == CodebaseClonerProtocolType.HTTPS
    assert codebase_cloner._get_protocol("http://github.com/user/repo.git") == CodebaseClonerProtocolType.HTTP


def test_is_archive(codebase_cloner):
    # Test Positive cases
    assert codebase_cloner._is_archive("/path/to/archive.zip") is True, "Expected to be an archive"
    assert codebase_cloner._is_archive("/path/to/archive.tar") is True, "Expected to be an archive"
    assert codebase_cloner._is_archive("/path/to/archive.tar.gz") is True, "Exeptected to be an archive"
    assert codebase_cloner._is_archive("/path/to/archive.tgz") is True, "Expected to be an archive"
    assert codebase_cloner._is_archive("/path/to/archive.tar.bz2") is True, "Expected to be an archive"
    assert codebase_cloner._is_archive("/path/to/archive.tbz2") is True, "Expected to be an archive"

    # Test negative cases
    assert codebase_cloner._is_archive("/path/to/file.py") is False, "Expected not to be an archive"
    assert codebase_cloner._is_archive("/path/to/dir") is False, "Expected not to be an archive"


def test_get_archive_type(codebase_cloner):
    assert codebase_cloner._get_archive_type("/path/to/archive.zip") == ArchiveType.ZIP
    assert codebase_cloner._get_archive_type("/path/to/archive.tar") == ArchiveType.TAR
    assert codebase_cloner._get_archive_type("/path/to/archive.tar.gz") == ArchiveType.TAR_GZ
    assert codebase_cloner._get_archive_type("/path/to/archive.tgz") == ArchiveType.TAR_GZ
    assert codebase_cloner._get_archive_type("/path/to/archive.tar.bz2") == ArchiveType.TAR_BZ2
    assert codebase_cloner._get_archive_type("/path/to/archive.tbz2") == ArchiveType.TAR_BZ2
    assert codebase_cloner._get_archive_type("/path/to/unknown.ext") == ArchiveType.UNKNOWN


@pytest.mark.asyncio
async def test_extract_archive_zip_success(codebase_cloner):
    archive_path = Path("/source/archive.zip")
    dest_path = PathUtil.get_codebase_repositories_AnalyticQ_path() / "archive"

    # Mock the necessary dependencies
    with patch('analyticq.util.PathUtil.get_codebase_repositories_AnalyticQ_path', return_value=dest_path.parent), \
         patch.object(Path, 'exists', side_effect=[True, False]), \
         patch.object(CodebaseCloner, '_get_archive_type', return_value=ArchiveType.ZIP), \
         patch('os.makedirs') as mock_makedirs, \
         patch('zipfile.ZipFile') as mock_zipfile, \
         patch('asyncio.to_thread') as mock_to_thread:

        # Configure mock behavior
        mock_zipfile_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zipfile_instance

        # Call the method
        result = await codebase_cloner.extract_archive(str(archive_path))

        # Verify the correct calls were made
        mock_makedirs.assert_called_once_with(dest_path, exist_ok=True)
        mock_zipfile.assert_called_once_with(archive_path, 'r')
        mock_to_thread.assert_called_once_with(mock_zipfile_instance.extractall, dest_path)
        assert result == dest_path


@pytest.mark.asyncio
async def test_extract_archive_tar_success(codebase_cloner):
    archive_path = Path("/source/archive.tar.gz")
    dest_path = PathUtil.get_codebase_repositories_AnalyticQ_path() / "archive"

    # Mock the necessary dependencies
    with patch('analyticq.util.PathUtil.get_codebase_repositories_AnalyticQ_path', return_value=dest_path.parent), \
         patch.object(Path, 'exists', side_effect=[True, False]), \
         patch.object(CodebaseCloner, '_get_archive_type', return_value=ArchiveType.TAR_GZ), \
         patch('os.makedirs') as mock_makedirs, \
         patch('tarfile.open') as mock_tarfile, \
         patch('asyncio.to_thread') as mock_to_thread:

        # Configure mock behavior
        mock_tarfile_instance = MagicMock()
        mock_tarfile.return_value.__enter__.return_value = mock_tarfile_instance

        # Call the method
        result = await codebase_cloner.extract_archive(str(archive_path))

        # Verify the correct calls were made
        mock_makedirs.assert_called_once_with(dest_path, exist_ok=True)
        mock_tarfile.assert_called_once_with(archive_path)
        mock_to_thread.assert_called_once_with(mock_tarfile_instance.extractall, dest_path)
        assert result == dest_path


@pytest.mark.asyncio
async def test_clone_remote_repo(codebase_cloner):
    codebase_url = "https://github.com/fake/repo.git"
    branch = "main"
    repo_name = "repo"
    expected_repo_path = PathUtil.get_codebase_repositories_AnalyticQ_path() / repo_name

    with patch('analyticq.util.PathUtil'), \
         patch("pathlib.Path.exists", return_value=False), \
         patch("git.Repo.clone_from"), \
         patch.object(CodebaseCloner, 'clone_remote_codebase', return_value=expected_repo_path) as mock_clone_remote:

        result_path = await codebase_cloner.clone(codebase_url, branch=branch)
        assert result_path == expected_repo_path, f"Expected {expected_repo_path}, got {result_path}"
        mock_clone_remote.assert_called_once_with(codebase_url, branch, None, None, CodebaseClonerProtocolType.HTTPS)


@pytest.mark.asyncio
async def test_clone_local_repo(codebase_cloner):
    codebase_url = "home/local/repo"
    expected_repo_path = PathUtil.get_codebase_repositories_AnalyticQ_path() / Path(codebase_url).name

    with patch('analyticq.util.PathUtil'), \
         patch("os.path.exists", return_value=True), \
         patch("pathlib.Path.exists", return_value=True), \
         patch("shutil.copytree"), \
         patch.object(CodebaseCloner, '_get_codebase_type', return_value=CodebaseClonerPathType.LOCAL_REPO), \
         patch.object(CodebaseCloner, 'clone_local_codebase', return_value=expected_repo_path) as mock_clone_local:

        result_path = await codebase_cloner.clone(codebase_url)
        assert result_path == expected_repo_path, f"Expected {expected_repo_path}, got {result_path}"
        mock_clone_local.assert_called_once_with(codebase_url)


@pytest.mark.asyncio
async def test_clone_local_script(codebase_cloner):
    codebase_url = "/local/script.py"
    expected_script_path = PathUtil.get_codebase_scripts_AnalyticQ_path() / Path(codebase_url).name

    with patch('analyticq.util.PathUtil'), \
         patch("pathlib.Path.exists", side_effect=[True, False]), \
         patch("shutil.copy"), \
         patch.object(CodebaseCloner, '_get_codebase_type', return_value=CodebaseClonerPathType.SCRIPT), \
         patch.object(CodebaseCloner, 'clone_local_script', return_value=expected_script_path) as mock_clone_script:

        result_path = await codebase_cloner.clone(codebase_url)
        assert result_path == expected_script_path, f"Expected {expected_script_path}, git {result_path}"
        mock_clone_script.assert_called_once_with(codebase_url)


@pytest.mark.asyncio
async def test_extract_archive_file_not_found(codebase_cloner):
    archive_path = Path("/source/nonexistent.zip")

    with patch.object(Path, 'exists', return_value=False):
        with pytest.raises(CodebaseNotFoundException):
            await codebase_cloner.extract_archive(str(archive_path))


@pytest.mark.asyncio
async def test_extract_archive_unsupported_format(codebase_cloner):
    archive_path = Path("/source/unknown.format")

    with patch.object(Path, 'exists', return_value=True), \
         patch.object(CodebaseCloner, '_get_archive_type', return_value=ArchiveType.UNKNOWN):

        with pytest.raises(ExtractArchiveException):
            await codebase_cloner.extract_archive(str(archive_path))


@pytest.mark.asyncio
async def test_clone_with_archive(codebase_cloner):
    archive_path = "/source/archive.zip"
    expected_dest_path = PathUtil.get_codebase_repositories_AnalyticQ_path() / "archive"

    with patch('analyticq.util.PathUtil'), \
         patch.object(CodebaseCloner, '_get_codebase_type', return_value=CodebaseClonerPathType.ARCHIVE), \
         patch.object(CodebaseCloner, 'extract_archive', return_value=expected_dest_path) as mock_extract_archive:

        result_path = await codebase_cloner.clone(archive_path)

        assert result_path == expected_dest_path, f"Expected {expected_dest_path}, got {result_path}"
        mock_extract_archive.assert_called_once_with(archive_path)


@pytest.mark.asyncio
async def test_clone_unknown_type(codebase_cloner):
    codebase_url = "/unknown/path"

    with patch('analyticq.util.PathUtil'), \
         patch("pathlib.Path.exists", return_value=False), \
         patch.object(CodebaseCloner, '_get_codebase_type', return_value=CodebaseClonerPathType.UNKNOWN):

        with pytest.raises(CodebaseUnknownTypeException):
            await codebase_cloner.clone(codebase_url)
