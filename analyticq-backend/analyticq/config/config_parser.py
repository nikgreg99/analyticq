import json
from typing import Any, Dict

import yaml


class AnalyticQConfigParser:
    """
    A class to parse configuration files in JSON or YAML format.
    """
    @staticmethod
    def parse(file, conf_path: str) -> Dict[str, Any]:
        """
        Parse a configuration file based on its extension (JSON or YAML).

        Args:
            file: A file object to read the configuration data from.
            conf_path: The path of the configuration file (used to determine the extension).

        Returns:
            dict: A dictionary representing the parsed configuration data.
        """
        SUPPORTED_FORMATS = {"json": json.load, "yaml": yaml.safe_load, "yml": yaml.safe_load}
        ext = conf_path.rsplit(".", 1)[-1]
        if ext in SUPPORTED_FORMATS:
            return SUPPORTED_FORMATS[ext](file)
        raise ValueError(f"Unsupported file format: {ext}")
