import json
import logging

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
    def get_default_AnalyticQ_config_filename(config_file_format: str = AnalyticQConst.JSON_EXTENSION) -> str:
        extensions = {
            AnalyticQConst.JSON_EXTENSION: f"{AnalyticQConst.DEFAULT_ANALYTICQ_CONFIG_FILE}.{AnalyticQConst.JSON_EXTENSION}",
            AnalyticQConst.YAML_EXTENSION: f"{AnalyticQConst.DEFAULT_ANALYTICQ_CONFIG_FILE}.{AnalyticQConst.YAML_EXTENSION}",
        }
        return extensions.get(config_file_format, f"{AnalyticQConst.DEFAULT_ANALYTICQ_CONFIG_FILE}.{AnalyticQConst.YML_EXTENSION}")
