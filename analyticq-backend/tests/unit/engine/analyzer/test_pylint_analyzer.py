from pathlib import Path
from unittest.mock import AsyncMock, Mock

import pytest
from analyticq.engine.analyzer.python import PylintAnalyzer
from analyticq.manager import AnalyticQContainerManager


@pytest.fixture
def container_manager():
    return Mock(spec=AnalyticQContainerManager)


@pytest.fixture
def analyzer(container_manager):
    return PylintAnalyzer(
        container_manager=container_manager,
        image_name="pylint",
        image_tag="latest"
    )


@pytest.mark.asyncio
async def test_run_analysis_basic(analyzer, container_manager):
    # Setup
    codebase_path = "/fake/path"
    expected_results = {"issues": []}

    container_manager.run_container_command = AsyncMock(return_value=expected_results)

    # Execute
    results = await analyzer.run_analysis(codebase_path)

    # Verify
    assert results == expected_results
    container_manager.run_container_command.assert_called_once()

    # Check that the volumes were set up correctly
    call_kwargs = container_manager.run_container_command.call_args[1]
    volumes = call_kwargs['volumes']
    assert codebase_path in volumes
    assert volumes[codebase_path]['bind'] == '/code'
    assert volumes[codebase_path]['mode'] == 'ro'


@pytest.mark.asyncio
async def test_run_analysis_with_config(analyzer, container_manager):
    # Setup
    codebase_path = "/fake/path"
    config_path = "/fake/config/.pylintrc"
    container_manager.run_container_command = AsyncMock(return_value={})

    # Execute
    await analyzer.run_analysis(codebase_path, config_path=config_path)

    # Verify
    call_kwargs = container_manager.run_container_command.call_args[1]
    volumes = call_kwargs['volumes']
    assert config_path in volumes
    assert volumes[config_path]['bind'] == '.pylintrc'
    assert volumes[config_path]['mode'] == 'ro'


@pytest.mark.asyncio
async def test_run_analysis_with_real_tempdir(analyzer, container_manager):

    codebse_path = "/fake/path"
    container_manager.run_container_command = AsyncMock(return_value={})

    await analyzer.run_analysis(codebse_path)

    call_kwargs = container_manager.run_container_command.call_args[1]
    volumes = call_kwargs['volumes']

    output_volume = next(v for v in volumes.keys() if isinstance(v, Path))
    assert volumes[output_volume]['bind'] == '/output'
    assert volumes[output_volume]['mode'] == 'rw'


@pytest.mark.asyncio
async def test_run_analysis_container_failure(analyzer, container_manager):
    codebase_path = "/fake/path"
    container_manager.run_container_command = AsyncMock(side_effect=Exception("Container failed"))

    with pytest.raises(Exception, match="Container failed"):
        await analyzer.run_analysis(codebase_path)
