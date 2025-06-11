import asyncio
import subprocess
from unittest.mock import AsyncMock, MagicMock, patch

import aiodocker
import pytest
from analyticq.exception import DockerNotFoundException
from analyticq.manager import DockerImageManager, DockerRegistryConfig


@pytest.fixture
def mock_docker():
    """Create a mock Docker client."""
    mock = MagicMock()
    mock.images = AsyncMock()
    return mock


@pytest.fixture
def image_manager(mock_docker):
    """Create an ImageManager instance with a mock Docker client."""
    return DockerImageManager(mock_docker)


@pytest.fixture
def docker_registry_config():
    return DockerRegistryConfig(
        registry="https://registry.example.com",
        username="testuser",
        password="testpassword",
    )


@pytest.mark.asyncio
async def test_docker_available(image_manager):
    with patch("asyncio.to_thread") as mock_create_subprocess_exec:
        # Mock the subprocess to simulate a successful Docker check
        mock_process = AsyncMock()
        mock_process.returncode = 0
        mock_process.communicate.return_value = (b"Docker version 20.10.17", b"")
        mock_create_subprocess_exec.return_value = mock_process

        result = await image_manager.check_docker_availability()
        assert result is True, "Expected Docker to be installed on the system"


@pytest.mark.asyncio
async def test_docker_not_available(image_manager):
    with patch("asyncio.to_thread") as mock_create_subprocess_exec:
        mock_process = AsyncMock()
        mock_process.returncode = 1
        mock_process.communicate.return_value = (b"", b"Docker command not found")
        mock_create_subprocess_exec.return_value = mock_process

        with pytest.raises(DockerNotFoundException):
            await image_manager.check_docker_availability()


@pytest.mark.asyncio
async def test_docker_command_not_found(image_manager):
    with patch("asyncio.to_thread") as mock_create_subprocess_exec:
        mock_create_subprocess_exec.side_effect = FileNotFoundError("Docker command not found")

        with pytest.raises(DockerNotFoundException):
            await image_manager.check_docker_availability()


@pytest.mark.asyncio
async def test_exists_image_found(image_manager, mock_docker):
    """Test exists() when image is found."""
    mock_docker.images.get = AsyncMock(return_value={"Id": "123"})

    result = await image_manager.exists("test-image", "latest")

    assert result is True, "Expected image found"
    mock_docker.images.get.assert_called_once_with("test-image:latest")


@pytest.mark.asyncio
async def test_exists_image_not_found(image_manager, mock_docker):
    """Test exists() when image is not found."""
    mock_docker.images.get = AsyncMock(
        side_effect=aiodocker.exceptions.DockerError("Error", data={"message": "Image not found"})
    )

    result = await image_manager.exists("test-image", "latest")

    assert result is False
    mock_docker.images.get.assert_called_once_with("test-image:latest")


@pytest.mark.asyncio
async def test_exists_default_tag(image_manager, mock_docker):

    mock_docker.images.get = AsyncMock(return_value={"Id": "123"})

    result = await image_manager.exists("test-image")

    assert result is True
    mock_docker.images.get.assert_called_once_with("test-image:latest")


@pytest.mark.asyncio
async def test_pull_succesfull_image(image_manager, mock_docker):

    mock_docker.images.pull = AsyncMock()

    await image_manager.pull("test-image", "v1.0")

    mock_docker.images.pull.assert_called_once_with("test-image", tag="v1.0", auth=None)


@pytest.mark.parametrize("image_name, image_tag, expected_id", [
    ("nginx", "latest", "123abc"),
    ("python", "latest", "456def"),
    ("ubuntu", "20.04", "789ghi")
])
@pytest.mark.asyncio
async def test_exists_various_images(image_manager, mock_docker, image_name, image_tag, expected_id):
    """Test exists() with various image names and tags."""

    # Arrange
    mock_docker.images.get = AsyncMock(return_value={"Id": expected_id})
    expected_image_reference = f"{image_name}:{image_tag}"

    # Act
    result = await image_manager.exists(image_name, image_tag)

    # Assert
    assert result is True, f"Expected {expected_image_reference} to exist"
    mock_docker.images.get.assert_called_once_with(expected_image_reference)


@pytest.mark.asyncio
async def test_pull_none_values(image_manager, mock_docker):
    """Test pull() with None values."""
    with pytest.raises(ValueError):
        await image_manager.pull(None, "latest")

    with pytest.raises(ValueError):
        await image_manager.pull("test-image", None)


@pytest.mark.asyncio
async def test_login_successful(image_manager, docker_registry_config):
    with patch("asyncio.to_thread") as mock_subprocess:
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=(b"", b""))
        mock_process.returncode = 0
        mock_subprocess.return_value = mock_process

        # Call the login method
        result = await image_manager.login(docker_registry_config)

        assert result is True, "Expected login to be successful"
        mock_subprocess.assert_called_once_with(
            subprocess.run,
            ["docker", "login", docker_registry_config.registry, "--username", docker_registry_config.username,
                "--password-stdin"],
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        mock_subprocess.assert_called_once_with(
            subprocess.run,
            ["docker", "login", docker_registry_config.registry, "--username", docker_registry_config.username,
                "--password-stdin"],
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )


@pytest.mark.asyncio
async def test_login_failed(image_manager, docker_registry_config):
    with patch("asyncio.to_thread") as mock_subprocess:
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value={b"", b"Login failed"})
        mock_process.returncode = 1
        mock_subprocess.return_value = mock_process

        result = await image_manager.login(docker_registry_config)

        assert result is False, "Exptected login to fail"
        mock_subprocess.assert_called_once_with(
            subprocess.run,
            ["docker", "login", docker_registry_config.registry, "--username", docker_registry_config.username,
             "--password-stdin"],
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        assert image_manager.auth_config is None


@pytest.mark.asyncio
async def test_logout_successful(image_manager, docker_registry_config):
    with patch("asyncio.to_thread") as mock_subprocess:
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=(b"", b""))
        mock_process.returncode = 0
        mock_subprocess.return_value = mock_process

        await image_manager.login(docker_registry_config)


@pytest.mark.asyncio
async def test_logout_failed(image_manager, docker_registry_config):
    # First, log in to the set
    with patch("asyncio.to_thread") as mock_subprocess:
        mock_process = AsyncMock()
        mock_process.communicare = AsyncMock(return_value=(b"", b"Logout failed"))
        mock_process.return_code = 0
        mock_subprocess.return_value = mock_process

        await image_manager.login(docker_registry_config)

    with patch("asyncio.to_thread") as mock_subprocess:
        mock_process = AsyncMock()
        mock_process.communicate = AsyncMock(return_value=(b"", b"Logout failed"))
        mock_process.returncode = 1
        mock_subprocess.return_value = mock_process

        with pytest.raises(RuntimeError):
            await image_manager.logout()

        mock_subprocess.assert_not_called()

        assert image_manager.auth_config is None


@pytest.mark.asyncio
async def test_logout_without_login(image_manager):
    """Test logout() when no login has been performed."""
    with pytest.raises(Exception):
        await image_manager.logout()

    # Assertions
    assert image_manager.auth_config is None
