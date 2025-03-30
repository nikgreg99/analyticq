import importlib
from unittest import mock

import pytest
from analyticq.engine import AnalyticQSASToolRegistry, AnalyticQToolDiscoverer


@pytest.fixture(autouse=True)
def reset_registry():
    """Fixture to reset the tool registry before each test."""
    AnalyticQSASToolRegistry._registered_tool_classes = {}
    yield
    AnalyticQSASToolRegistry._registered_tool_classes = {}


@pytest.fixture
def mock_base_package():
    """Fixture to create a mock package."""
    mock_pkg = mock.MagicMock()
    mock_pkg.__path__ = ['/mock/path']
    return mock_pkg


@pytest.fixture
def mock_imports(monkeypatch, mock_base_package):
    mock_import = mock.MagicMock()
    mock_import.return_value = mock_base_package
    monkeypatch.setattr(importlib, 'import_module', mock_import)
    return mock_import


@pytest.fixture
def mock_pkg_iter(monkeypatch):
    mock_iter = mock.MagicMock()
    mock_iter.return_value = []
    monkeypatch.setattr('pkgutil.iter_modules', mock_iter)
    return mock_iter


@pytest.fixture
def mock_logger(monkeypatch):
    mock_log = mock.MagicMock()
    mock_logger_instance = mock.MagicMock()
    mock_log.return_value = mock_logger_instance
    monkeypatch.setattr("logging.getLogger", mock_log)
    return mock_logger_instance


def test_discover_empty_package(reset_registry, mock_imports, mock_pkg_iter):
    AnalyticQToolDiscoverer.discover_and_register_tools()

    # Verify no tools were registered
    assert len(AnalyticQSASToolRegistry._registered_tool_classes) == 0
    mock_imports.assert_called_with("analyticq.engine.tools")
