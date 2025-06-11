import json
from pathlib import Path
from typing import Any, Dict, TextIO, Union

import yaml


class AnalyticQConfigParser:
    """
    A class to parse configuration files in JSON or YAML format.
    """

    SUPPORTED_FORMATS = {
        "json": json.load,
        "yaml": yaml.safe_load,
        "yml": yaml.safe_load
    }

    @staticmethod
    def parse(file: TextIO, conf_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Parse a configuration file based on its extension (JSON or YAML).

        Args:
            file: A file object to read the configuration data from.
            conf_path: The path of the configuration file (used to determine the extension).

        Returns:
            dict: A dictionary representing the parsed configuration data.
        """
        ext = Path(conf_path).suffix.lstrip('.').lower()
        parser = AnalyticQConfigParser.SUPPORTED_FORMATS.get(ext)

        if parser is None:
            raise ValueError(f"Unsupported file format: {ext}")

        try:
            return parser(file)
        except Exception as e:
            raise ValueError(f"Failed to parse configuration file '{conf_path}': {e}") from e
