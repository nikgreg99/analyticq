from unittest.mock import mock_open, patch

import pytest
from analyticq.config import AnalyticQConfigParser

# Mock data for testing
json_data = '{"key1": "value1", "key2": "value2"}'
yaml_data = "key1: value1\nkey2: value2"


@pytest.mark.parametrize("file_data, ext, expected", [
    (json_data, "json", {"key1": "value1", "key2": "value2"}),
    (yaml_data, "yaml", {"key1": "value1", "key2": "value2"}),
    (yaml_data, "yml", {"key1": "value1", "key2": "value2"})
])
def test_config_parser(file_data, ext, expected):
    with patch("builtins.open", mock_open(read_data=file_data)):
        parsed_data = AnalyticQConfigParser.parse(mock_open(read_data=file_data)(), f"config.{ext}")
        assert parsed_data == expected, f"Expected {parsed_data}, got {expected}"


def test_invalid_extension():
    with patch("builtins.open", mock_open(read_data=json_data)):
        with pytest.raises(ValueError):
            AnalyticQConfigParser.parse(mock_open(read_data=json_data)(), "config.txt")
