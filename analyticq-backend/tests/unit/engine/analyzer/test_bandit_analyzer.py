from pathlib import Path
from unittest.mock import MagicMock

import pytest
from analyticq.engine.analyzer import BanditAnalyzer
from analyticq.manager import AnalyticQContainerManager


@pytest.fixture
def container_manager():
    return MagicMock(spec=AnalyticQContainerManager)


@pytest.fixture
def analyzer(container_manager):
    return BanditAnalyzer(
        container_manager=container_manager,
        image_name="bandit",
        image_tag="latest"
    )


@pytest.mark.asyncio
async def test_run_analysis_basic(analyzer, container_manager):

    """Test basic analysis run without config file"""

    code_path = "/path/to/code"

    await analyzer.run_analysis(codebase_path=code_path)

    # Verify container manager was called correctly
    container_manager.run_container_command.assert_called_once()
    call_args = container_manager.run_container_command.call_args[1]
    assert call_args["image_name"] == "bandit"
    assert call_args["image_tag"] == "latest"
    assert call_args["command_args"] == []
    assert "/code" in call_args["volumes"][code_path]["bind"]
    assert call_args["volumes"][code_path]["mode"] == "ro"


@pytest.mark.asyncio
async def test_run_analysis_with_real_tmpdir(analyzer, container_manager):
    code_path = "/path/to/code"

    await analyzer.run_analysis(codebase_path=code_path)

    call_args = container_manager.run_container_command.call_args[1]
    volumes = call_args["volumes"]

    for path, config in volumes.items():
        if isinstance(path, Path):
            temp_volume_entry = config
            break

    # Assert
    assert temp_volume_entry is not None, "No temporary directory found in volumes"
    assert temp_volume_entry["bind"] == "/output"
    assert temp_volume_entry["mode"] == "rw"
