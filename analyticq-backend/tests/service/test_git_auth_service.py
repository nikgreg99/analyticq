import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from analyticq.service import GitAuthService


@pytest.fixture
def mock_ssh_key_path(tmp_path):
    """Create a mock SSH key for testing."""
    key_path = tmp_path / "id_rsa"
    key_path.write_text("mock_ssh_key_content")
    return str(key_path)


@pytest.mark.parametrize(
    ("system", "outcome"),
    [
        ("Windows", True),
        ("Linux", False)
    ]
)
def test_is_windows(system, outcome):
    """Test platform detection method."""
    with patch('platform.system', return_value=system):
        service = GitAuthService()
        result = service._is_windows()
        assert result == outcome, f"Expected {system}, got {outcome}"


def test_start_ssh_agent_windows():
    with patch('subprocess.run') as mock_run:
        service = GitAuthService()
        with patch('platform.system', return_value='Windows'):
            service._start_ssh_agent()
            mock_run.assert_called_once_with(
                ["sc", "start", "ssh-agent"],
                capture_output=True,
                check=True
            )


def test_start_ssh_agent_unix():
    with patch('subprocess.run') as mock_run, \
         patch.dict(os.environ, {}, clear=True):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="SSH_AUTH_SOCK=test_sock;"
        )
        service = GitAuthService()
        with patch('platform.system', return_value='Linux'):
            service._start_ssh_agent()
            assert os.environ.get("SSH_AUTH_SOCK") == "test_sock"


def test_key_is_loaded(mock_ssh_key_path):
    with patch("subprocess.run") as mock_run:
        service = GitAuthService()

        mock_run.return_value = MagicMock(
            stdout=mock_ssh_key_path,
            returncode=0
        )

        result = service._is_key_loaded(mock_ssh_key_path)
        assert result is True, f"Expected True for {mock_ssh_key_path}, got {result}"


def test_key_is_not_loaded(mock_ssh_key_path):
    with patch("subprocess.run") as mock_run:
        service = GitAuthService()
        mock_run.return_value = MagicMock(
            stdout="",
            returncode=1
        )

        result = service._is_key_loaded(mock_ssh_key_path)
        assert result is False, f"Expected True for {mock_ssh_key_path}, got {result}"


def test_load_ssh_key(mock_ssh_key_path):
    with patch("subprocess.run") as mock_run, \
         patch.object(Path, "exists", return_value=True):

        service = GitAuthService()
        # Simulate successful key loading
        mock_run.return_value = MagicMock(returncode=0)

        service.load_ssh_key(Path(mock_ssh_key_path))

        # Verify ssh-add was called
        mock_run.assert_called_with(
            ["ssh-add", mock_ssh_key_path],
            check=True
        )


@pytest.mark.skip("to be fix")
def test_configure_git_ssh(mock_ssh_key_path):
    service = GitAuthService()

    # Mock key loading methods
    with patch.object(service, '_is_key_loaded', return_value=False), \
         patch('subprocess.run') as mock_run, \
         patch.dict(os.environ, {}, clear=True):

        # Mock successful key loading
        mock_run.return_value = MagicMock(returncode=0)

        # Ensure key is loaded before configuration
        service.load_ssh_key(Path(mock_ssh_key_path))
        service.configure_git_ssh(Path(mock_ssh_key_path))

        assert os.environ["GIT_SSH_COMMAND"] == \
            f"ssh -i {mock_ssh_key_path} -o IdentitiesOnly=yes"


def test_configure_git_ssh_key_already_loaded(mock_ssh_key_path):

    service = GitAuthService()

    # Mock key already loaded
    with patch.object(service, '_is_key_loaded', return_value=True), \
         patch.dict(os.environ, {}, clear=True):

        service.configure_git_ssh(Path(mock_ssh_key_path))

        assert os.environ["GIT_SSH_COMMAND"] == \
            f"ssh -i {mock_ssh_key_path} -o IdentitiesOnly=yes"


def test_missing_ssh_key(mock_ssh_key_path):
    with patch.object(Path, "exists", return_value=False):
        service = GitAuthService()

        with pytest.raises(FileNotFoundError):
            service.load_ssh_key(Path(mock_ssh_key_path))
