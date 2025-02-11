import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import aiodocker
import pytest
from analyticq.exception import ScanConfigurationException
from analyticq.manager import AnalyticQContainerManager


@pytest.fixture
async def container_manager():
    async with AnalyticQContainerManager() as manager:
        yield manager


@pytest.mark.asyncio
async def test_image_exists(container_manager):
    with patch.object(container_manager.docker.images, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {'Id': 'some-id'}
        assert await container_manager._image_exists('test-image', 'latest') is True, "Expected True for existing test image"
        mock_get.assert_called_once_with('test-image:latest')


@pytest.mark.asyncio
async def test_image_not_exist(container_manager):
    with patch.object(container_manager.docker.images, 'get', new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = aiodocker.exceptions.DockerError(404, {'message': 'Not found'})
        assert await container_manager._image_exists('nonexistent-image') is False, "Expected False for non existing image"


@pytest.mark.asyncio
async def test_pull_image(container_manager):
    with patch.object(container_manager.docker.images, 'pull', new_callable=AsyncMock) as mock_pull:
        await container_manager.pull_image('test-image', 'latest')
        mock_pull.assert_called_once_with('test-image', tag='latest')


@pytest.mark.asyncio
async def test_pull_image_failure(container_manager):
    with patch.object(container_manager.docker.images, 'pull', new_callable=AsyncMock) as mock_pull:
        mock_pull.side_effect = aiodocker.exceptions.DockerError(500, {'message': 'Pull failed'})
        with pytest.raises(RuntimeError, match='Failed to pull image'):
            await container_manager.pull_image('test-image', 'latest')


@pytest.mark.asyncio
async def test_run_container_command(container_manager, tmpdir):
    # Create a mock container
    mock_container = AsyncMock()
    mock_container.start = AsyncMock()
    mock_container.wait = AsyncMock(return_value={'StatusCode': 0})
    mock_container.delete = AsyncMock()

    # Mock container creation
    with patch.object(container_manager.docker.containers, 'create', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_container

        # Create a temporary directory for volume testing
        tmp_path = Path(tempfile.gettempdir()) / 'test'
        tmp_path.mkdir(exist_ok=True)

        volumes = {
            tmp_path: {
                "bind": "/container/path",
                "mode": "ro"
            }
        }

        await container_manager.run_container_command(
            image_name='test-image',
            image_tag='latest',
            command_args=['echo', 'hello'],
            volumes=volumes,
            env_vars={'TEST_VAR': 'test_value'}
        )

        # Verify the container was created with correct parameters
        mock_create.assert_called_once()
        create_args = mock_create.call_args[1]['config']
        assert create_args['Image'] == 'test-image:latest'
        assert create_args['Cmd'] == ['echo', 'hello']
        assert 'TEST_VAR=test_value' in create_args['Env']


@pytest.mark.asyncio
async def test_run_container_invalid_volume(container_manager):
    with pytest.raises(ScanConfigurationException, match="Invalid host path"):
        await container_manager.run_container_command(
            image_name='test-image',
            volumes={Path('/nonexistent/path'): {"bind": "/container/path", "mode": "ro"}}
        )
