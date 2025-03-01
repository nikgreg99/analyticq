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


async def test_pull_none_values(image_manager, mock_docker):
    """Test pull() with None values."""
    with pytest.raises(ValueError):
        await image_manager.pull(None, "latest")

    with pytest.raises(ValueError):
        await image_manager.pull("test-image", None)
