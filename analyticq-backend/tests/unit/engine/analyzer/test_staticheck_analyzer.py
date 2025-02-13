from unittest.mock import AsyncMock, Mock

import pytest
from analyticq.engine.analyzer import StaticCheckAnalyzer
from analyticq.engine.core.analyzer import AnalyticQAnalyzer
from analyticq.manager import AnalyticQContainerManager


@pytest.fixture
def mock_container_manager():
    return Mock(spec=AnalyticQContainerManager)


@pytest.fixture
def analyzer(mock_container_manager):
    return StaticCheckAnalyzer(
        container_manager=mock_container_manager,
        image_name="staticcheck",
        image_tag="latest"
    )


def test_initialization(analyzer):
    """Test if the analyzer is initialized with correct attributes"""
    assert isinstance(analyzer, AnalyticQAnalyzer)
    assert analyzer.image_name == "staticcheck"
    assert analyzer.image_tag == "latest"
    assert analyzer.staticceck_output_file == "staticcheck-report.json"


@pytest.mark.asyncio
async def test_run_analysis_without_config(analyzer, mock_container_manager):
    """Test running analysis without a config file"""
    # Setup
    codebase_path = "/path/to/code"
    expected_results = []
    mock_container_manager.run_container_command = AsyncMock(return_value=[])

    # Execute
    result = await analyzer.run_analysis(codebase_path=codebase_path)

    # Verify
    mock_container_manager.run_container_command.assert_called_once()
    call_kwargs = mock_container_manager.run_container_command.call_args[1]

    assert call_kwargs["image_name"] == "staticcheck"
    assert call_kwargs["image_tag"] == "latest"
    assert isinstance(call_kwargs["volumes"], dict)
    assert codebase_path in call_kwargs["volumes"]
    assert call_kwargs["volumes"][codebase_path]["bind"] == "/code"
    assert call_kwargs["volumes"][codebase_path]["mode"] == "ro"
    assert result == expected_results


@pytest.mark.asyncio
async def test_run_analysis_with_config(analyzer, mock_container_manager):
    """Test running analysis with a config file"""
    # Setup
    codebase_path = "/path/to/code"
    config_path = "/path/to/config"

    # Execute
    await analyzer.run_analysis(
        codebase_path=codebase_path,
        config_path=config_path
    )

    # Verify
    mock_container_manager.run_container_command.assert_called_once()
    call_kwargs = mock_container_manager.run_container_command.call_args[1]

    # Verify config file is mounted
    assert config_path in call_kwargs["volumes"]
    assert call_kwargs["volumes"][config_path]["bind"] == "staticcheck.conf"
    assert call_kwargs["volumes"][config_path]["mode"] == "ro"


@pytest.mark.asyncio
async def test_run_analysis_raises_exception(analyzer, mock_container_manager):
    """Test that exceptions from container manager are propagated"""
    # Setup
    codebase_path = "/path/to/code"
    mock_container_manager.run_container_command.side_effect = Exception("Container error")

    # Verify exception is raised
    with pytest.raises(Exception, match="Container error"):
        await analyzer.run_analysis(codebase_path=codebase_path)
