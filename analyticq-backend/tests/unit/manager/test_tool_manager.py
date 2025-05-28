import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from analyticq.engine.core import AnalyticQSASToolRegistry
from analyticq.manager.tool_manager import AnalyticQSASTManager
from analyticq.preprocessing import CodebasePreprocessor

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent


# Fixture for AnalyticQSASTManager
@pytest.fixture
def sast_manager():
    """
    Fixture to provide an instance of AnalyticQSASTManager with mocked dependencies.
    """
    with patch('analyticq.config.AnalyticQBaseConfig.get') as mock_config:
        manager = AnalyticQSASTManager()
        mock_config.return_value = {"default_branch": "main"}
        manager.registry = MagicMock(spec=AnalyticQSASToolRegistry)
        manager.codebase_preprocesseor = MagicMock(spec=CodebasePreprocessor)
    return manager


# Fixture for mock codebase data
@pytest.fixture
def mock_codebase_data():
    """
    Fixture to provide mock codebase data for testing.
    """
    return {
        "files": {
            "python": [{"file_path": "src/main/utils.py"}, {"file_path": "src/main/helpers.py"}],
            "js": [{"file_path": "src/js/app.js"}],
        },
        "language_statistics": {
            "python": {"files": 2, "lines": 100},
            "javascript": {"files": 1, "lines": 50},
        },
    }


@pytest.mark.asyncio
@pytest.mark.skip(reason="no way of currently testing this")
async def test_scan_codebase(sast_manager, mock_codebase_data):
    sast_manager.codebase_preprocesseor.preprocess_codebase = AsyncMock(return_value=mock_codebase_data)

    sast_manager.registry.get_supported_languages.return_value = {"python", "js"}
    sast_manager.registry.get_tools_for_language.return_value = ["tool1", "tool2"]
    sast_manager.registry.get_tool_instance.return_value = AsyncMock()

    mock_tool = sast_manager.registry.get_tool_instance.return_value
    mock_tool.install = AsyncMock()
    mock_tool.run_scan = AsyncMock(return_value={"issues": 5})

    result = await sast_manager.scan_codebase(
        codebase_path="https://github.com/SmartData-Polito/cannypot",
        config_paths={"tool1": "config/path"},
        timeout=30
    )

    assert isinstance(result, dict)
    print(result)
    assert "python" in result

    mock_tool.install.assert_awaited()
    mock_tool.run_scan.assert_awaited()

    assert result["python"]["tools_run"] == ["tool1", "tool2"]
    assert result["python"]["root_folders"] == ["src\\main"]
    assert result["python"]["file_count"] == 2
    assert result["python"]["statistics"] == {"files": 2, "lines": 100}


@pytest.mark.skip(reason="no way of currently testing this")
def test_identify_root_folders(sast_manager, mock_codebase_data):
    """
    Test the identify_root_folders method of AnalyticQSASTManager.
    """
    result = sast_manager.identify_root_folders(mock_codebase_data)

    # Assertions
    assert isinstance(result, dict)
    assert result["python"] == ["src\\main"]


# Test map_lang_to_supported method
@pytest.mark.parametrize(
    "json_lang, supported_languages, expected",
    [
        ("Python", {"python", "javascript"}, "python"),
        ("C++", {"c++", "python"}, "c++"),
        ("unknown", {"python", "javascript"}, None),
    ],
)
def test_map_lang_to_supported(sast_manager, json_lang, supported_languages, expected):
    """
    Test the map_lang_to_supported method of AnalyticQSASTManager.
    """
    result = sast_manager.map_lang_to_supported(json_lang, supported_languages)
    assert result == expected, f"Expected {expected} mapping, got {result}"
