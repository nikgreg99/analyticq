from unittest.mock import AsyncMock, MagicMock

import aiodocker
import pytest
from analyticq.manager import DockerImageManager


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
    mock_docker.images.get_assert_called_once_with("test-image")


@pytest.mark.asyncio
async def test_pull_succesfull_image(image_manager, mock_docker):

    mock_docker.images.pull = AsyncMock()

    await image_manager.pull("test-image", "v1.0")

    mock_docker.images.pull.assert_called_once_with("test-image", tag="v1.0")


@pytest.mark.parametrize("image_name, tag", [
    ("nginx", "latest"),
    ("python", "3.9"),
    ("ubuntu", "20.04"),
    ("", "latest"),  # Edge case: empty image name
    ("test-image", ""),  # Edge case: empty tag
])
async def test_exists_various_images(image_manager, mock_docker, image_name, tag):
    """Test exists() with various image names and tags."""
    mock_docker.images.get = AsyncMock(return_value={"Id": "123"})

    result = await image_manager.exists(image_name, tag)

    assert result is True
    mock_docker.images.get.assert_called_once_with(f"{image_name}:{tag}")


async def test_pull_none_values(image_manager, mock_docker):
    """Test pull() with None values."""
    with pytest.raises(TypeError):
        await image_manager.pull(None, "latest")

    with pytest.raises(TypeError):
        await image_manager.pull("test-image", None)
