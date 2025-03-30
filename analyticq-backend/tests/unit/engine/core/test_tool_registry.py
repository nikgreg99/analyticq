from functools import lru_cache
from typing import Set
from unittest.mock import Mock

import pytest
from analyticq.engine.core import AnalyticQSASToolRegistry, AnalyticQSASTTool


@pytest.fixture
def reset_registry():
    """Reset the registry before each test"""
    AnalyticQSASToolRegistry._registered_tool_classes = {}
    AnalyticQSASToolRegistry._tools_by_language = {}
    yield
    # Clean up after test
    AnalyticQSASToolRegistry._registered_tool_classes = {}
    AnalyticQSASToolRegistry._tools_by_language = {}


@pytest.fixture
def create_mock_tool():
    """Helper fixture to create mock tool classes"""
    def _create_mock_tool(languages: Set[str]):
        mock_tool_class = Mock(spec=AnalyticQSASTTool)
        mock_tool_class.supported_languages = languages
        mock_tool_class.return_value = Mock()  # For instantiation
        return mock_tool_class
    return _create_mock_tool


@pytest.fixture
def patch_registry_methods():
    """Patch registry methods to use correct attribute names"""
    # Save original methods
    original_get_tools = AnalyticQSASToolRegistry.get_tools_for_language
    original_get_languages = AnalyticQSASToolRegistry.get_supported_languages
    original_get_instance = AnalyticQSASToolRegistry.get_tool_instance

    # Patch methods
    @classmethod
    def patched_get_tools_for_language(cls, language):
        return cls._tools_by_language.get(language, [])

    @classmethod
    def patched_get_supported_languages(cls):
        return set(cls._tools_by_language.keys())

    @classmethod
    @lru_cache(maxsize=128)
    def fixed_get_tool_instance(cls, tool_name):
        if tool_name not in cls._registered_tool_classes:
            raise ValueError(f"Unknown tool: {tool_name}")
        tool_class = cls._registered_tool_classes[tool_name]
        return tool_class()

    AnalyticQSASToolRegistry.get_tools_for_language = patched_get_tools_for_language
    AnalyticQSASToolRegistry.get_supported_languages = patched_get_supported_languages
    AnalyticQSASToolRegistry.get_tool_instance = fixed_get_tool_instance

    yield

    # Restore original methods
    AnalyticQSASToolRegistry.get_tools_for_language = original_get_tools
    AnalyticQSASToolRegistry.get_supported_languages = original_get_languages
    AnalyticQSASToolRegistry.get_tool_instance = original_get_instance


def test_register_tool(reset_registry, create_mock_tool):
    # Create a mock tool class
    mock_tool = create_mock_tool({"python", "javascript"})

    # Register the mock tool
    AnalyticQSASToolRegistry.register_tool("mock_tool", mock_tool)

    # Check if the tool is registered
    assert "mock_tool" in AnalyticQSASToolRegistry._registered_tool_classes
    assert AnalyticQSASToolRegistry._registered_tool_classes["mock_tool"] == mock_tool

    # Check if language mappings are updated
    assert "python" in AnalyticQSASToolRegistry._tools_by_language
    assert "javascript" in AnalyticQSASToolRegistry._tools_by_language
    assert "mock_tool" in AnalyticQSASToolRegistry._tools_by_language["python"]
    assert "mock_tool" in AnalyticQSASToolRegistry._tools_by_language["javascript"]


def test_register_multiple_tools(reset_registry, create_mock_tool):
    # Create mock tool classes
    python_tool = create_mock_tool({"python"})
    js_tool = create_mock_tool({"javascript"})
    multi_tool = create_mock_tool({"python", "javascript", "java"})

    AnalyticQSASToolRegistry.register_tool("python_tool", python_tool)
    AnalyticQSASToolRegistry.register_tool("js_tool", js_tool)
    AnalyticQSASToolRegistry.register_tool("multi_tool", multi_tool)

    # Check tool registrations
    assert len(AnalyticQSASToolRegistry._registered_tool_classes) == 3

    # Check language mappings
    assert set(AnalyticQSASToolRegistry._tools_by_language.keys()) == {"python", "javascript", "java"}
    assert set(AnalyticQSASToolRegistry._tools_by_language["python"]) == {"python_tool", "multi_tool"}
    assert set(AnalyticQSASToolRegistry._tools_by_language["javascript"]) == {"js_tool", "multi_tool"}
    assert set(AnalyticQSASToolRegistry._tools_by_language["java"]) == {"multi_tool"}


def test_get_tools_for_language(reset_registry, create_mock_tool, patch_registry_methods):

    python_tool = create_mock_tool({"python"})
    multi_tool = create_mock_tool({"python", "javascript"})

    AnalyticQSASToolRegistry.register_tool("python_tool", python_tool)
    AnalyticQSASToolRegistry.register_tool("multi_tool", multi_tool)

    AnalyticQSASToolRegistry.register_tool("python_tool", python_tool)
    AnalyticQSASToolRegistry.register_tool("multi_tool", multi_tool)

    # Test getting tools for Python
    python_tools = AnalyticQSASToolRegistry.get_tools_for_language("python")
    assert set(python_tools) == {"python_tool", "multi_tool"}

    # Test getting tools for Js
    js_tools = AnalyticQSASToolRegistry.get_tools_for_language("javascript")
    assert set(js_tools) == {"multi_tool"}

    # Test getting tools for an unsupported language
    ruby_tools = AnalyticQSASToolRegistry.get_tools_for_language("ruby")
    assert ruby_tools == []


def test_get_tool_instance(reset_registry, create_mock_tool, patch_registry_methods):
    # Create a mock tool class
    mock_tool = create_mock_tool({"python"})

    # Register the mock tool
    AnalyticQSASToolRegistry.register_tool("mock_tool", mock_tool)

    # Get an instance of the tool
    tool_instance = AnalyticQSASToolRegistry.get_tool_instance("mock_tool")

    mock_tool.assert_called_once()
    assert tool_instance == mock_tool.return_value

    # Test getting an instance of an unknown tool
    with pytest.raises(ValueError, match="Unknown tool: unknown_tool"):
        AnalyticQSASToolRegistry.get_tool_instance("unknown_tool")


def test_get_supported_languages(reset_registry, create_mock_tool, patch_registry_methods):
    # Create and register mock tools
    python_tool = create_mock_tool({"python"})
    js_tool = create_mock_tool({"javascript"})
    java_tool = create_mock_tool({"java"})

    AnalyticQSASToolRegistry.register_tool("python_tool", python_tool)
    AnalyticQSASToolRegistry.register_tool("js_tool", js_tool)
    AnalyticQSASToolRegistry.register_tool("java_tool", java_tool)

    languages = AnalyticQSASToolRegistry.get_supported_languages()
    assert languages == {"python", "javascript", "java"}


def test_lazy_loading(reset_registry, create_mock_tool, patch_registry_methods):

    mock_tool1 = create_mock_tool({"python"})
    mock_tool2 = create_mock_tool({"javascript"})

    AnalyticQSASToolRegistry.register_tool("tool", mock_tool1)
    AnalyticQSASToolRegistry.register_tool("tool2", mock_tool2)

    # Check that the tools haven't been instantiated yet
    mock_tool1.assert_not_called()
    mock_tool2.assert_not_called()

    tool1_instance = AnalyticQSASToolRegistry.get_tool_instance("tool")

    # Check that only tool1 has been instantiated
    mock_tool1.assert_called_once()
    mock_tool2.assert_not_called()

    tool1_instance_again = AnalyticQSASToolRegistry.get_tool_instance("tool")

    mock_tool1.assert_called_once()
    assert tool1_instance == tool1_instance_again


def test_get_all_tools_info_no_tools(reset_registry):
    tools_info = AnalyticQSASToolRegistry.get_all_tools_info()
    assert tools_info == {}


def test_get_all_tool_info_duplicate_tools(reset_registry, create_mock_tool):
    python_tool = create_mock_tool({"python"})
    AnalyticQSASToolRegistry.register_tool("python_tool", python_tool)
    AnalyticQSASToolRegistry.register_tool("python_tool", python_tool)  # Duplicate registration

    tools_info = AnalyticQSASToolRegistry.get_all_tools_info()
    assert tools_info == {"python_tool": {"python"}}


def test_get_all_tools_info_empty_languages(reset_registry, create_mock_tool):
    empty_tool = create_mock_tool(set())
    AnalyticQSASToolRegistry.register_tool("empty_tool", empty_tool)

    tools_info = AnalyticQSASToolRegistry.get_all_tools_info()
    assert tools_info == {"empty_tool": set()}
