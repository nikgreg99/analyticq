import json
import logging
import os
from pathlib import Path
from typing import Any, List

import aiofiles
import yaml

from .const import AnalyticQConst

logger = logging.getLogger(__name__)


class FileUtil:

    def parse_list_env(key: str, default: List[Any] = None) -> List[Any]:
        """Parse a list from an environment variable.
        This function attempts to parse a list from an environment variable in two ways:
        1. As a JSON array
        2. As a comma-separated string
        Args:
            key (str): The environment variable key to parse
            default (List[Any], optional): Default value to return if key doesn't exist or parsing fails.
                Defaults to None.
        Returns:
            List[Any]: The parsed list from the environment variable, or the default value if parsing fails.
                If default is None, returns an empty list.
        Examples:
            # JSON array in env var
            os.environ['MY_LIST'] = '[1, 2, 3]'
            _parse_list_env('MY_LIST')  # Returns [1, 2, 3]
            # Comma-separated string in env var
            os.environ['MY_LIST'] = 'a, b, c'
            _parse_list_env('MY_LIST')  # Returns ['a', 'b', 'c']
        """

        value = os.environ.get(key)
        if not value:
            return default or []

        try:
            parsed = json.loads(value)
            if isinstance(parsed, list):
                return parsed
        except json.JSONDecodeError:
            return [item.strip() for item in value.split(',') if item.strip()]

        return default or []

    @staticmethod
    def save_to_json(conf_file_path: str, config_data: dict):
        """
        Save the configuration data to a JSON file.

        Args:
            conf_file_path: The file path where the JSON config data will be saved
            config_data: The configuration data to be saved.

        Returns:
            None: If the configuration was saved successfully.

        Raises:
            Exception: If there is an error while saving the config data
        """
        try:
            with open(conf_file_path, "w") as conf_file:
                json.dump(config_data, conf_file , indent=4)
        except Exception:
            logger.error("Error saving configuration")
            return None

    @staticmethod
    def save_to_yaml(conf_file_path: str, config_data: str):
        """
            Save the configuration data to a YAML file.

            Args:
                conf_file_path: The file path where the YAML config data will be saved.
                config_data: The configuration data to be saved.

            Returns:
                None: If the configuration was saved successfully.

            Raises:
                Exception: If there is an error while saving the config data.
        """
        try:
            with open(conf_file_path, "w") as conf_file:
                yaml.dump(config_data, conf_file, default_flow_style=False, allow_unicode=True)
        except yaml.YAMLError as ex:
            logger.error(f"Error during YAML serialization: {ex}")
            raise
        except Exception as ex:
            logger.error(f"Unexpected error while saving configuration to YAML: {ex}")
            raise

    @staticmethod
    def get_default_AnalyticQ_config_filename(config_file_format: str = AnalyticQConst.JSON_EXTENSION) -> str:
        """
        Get the default AnalyticQ configuration filename based on the specified file format.

        Args:
            config_file_format (str): The desired configuration file format.
                                      Defaults to AnalyticQConst.JSON_EXTENSION.

        Returns:
            str: The default configuration filename with the appropriate extension.
        """
        extensions = {
            AnalyticQConst.JSON_EXTENSION: f"{AnalyticQConst.ANALYTICQ_DEFAULT_CONFIG_FILE}.{AnalyticQConst.JSON_EXTENSION}",
            AnalyticQConst.YAML_EXTENSION: f"{AnalyticQConst.ANALYTICQ_DEFAULT_CONFIG_FILE}.{AnalyticQConst.YAML_EXTENSION}",
        }
        return extensions.get(config_file_format, f"{AnalyticQConst.ANALYTICQ_DEFAULT_CONFIG_FILE}.{AnalyticQConst.YML_EXTENSION}")

    @staticmethod
    async def read_file_content(file_path: Path) -> str:
        """
        Reads the content of a file asynchronously.

        Args:
            file_path (Path): The path to the file to be read.

        Returns:
            str: The content of the file as a string.

        Raises:
            FileNotFoundError: If the specified file does not exist.
            PermissionError: If the program lacks permission to read the file.
        """
        async with aiofiles.open(file_path, mode="r", encoding="utf-8", errors="ignore") as f:
            return await f.read()

    @staticmethod
    async def count_lines(file_path: Path) -> int:
        """
        Counts the number of lines in a file.

        Args:
            file_path (Path): The path to the file to count lines from.

        Returns:
            int: The number of lines in the file. Returns 0 if the file cannot be read.

        Raises:
            Exception: Any exception that occurs during file reading is caught and logged.
        """
        try:
            content = await FileUtil.read_file_content(file_path)
            return len(content.splitlines())
        except Exception as e:
            logger.warning(f"Failed to count lines in {file_path}: {e}")
            return 0
