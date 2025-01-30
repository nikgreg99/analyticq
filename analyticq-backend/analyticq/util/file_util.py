import json
import logging

import yaml

from .const import AnalyticQConst

logger = logging.getLogger(__name__)


class FileUtil:

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
    def save_to_ymal(conf_file_path: str, config_data: str):
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
            AnalyticQConst.JSON_EXTENSION: f"{AnalyticQConst.DEFAULT_ANALYTICQ_CONFIG_FILE}.{AnalyticQConst.JSON_EXTENSION}",
            AnalyticQConst.YAML_EXTENSION: f"{AnalyticQConst.DEFAULT_ANALYTICQ_CONFIG_FILE}.{AnalyticQConst.YAML_EXTENSION}",
        }
        return extensions.get(config_file_format, f"{AnalyticQConst.DEFAULT_ANALYTICQ_CONFIG_FILE}.{AnalyticQConst.YML_EXTENSION}")
