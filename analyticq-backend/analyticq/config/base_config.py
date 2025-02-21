import logging
import os
from pathlib import Path
from typing import Any, Dict

from analyticq.util import FileUtil, PathUtil
from pydantic import BaseModel

from .config_parser import AnalyticQConfigParser
from .env_loader import AnalyticQEnvironmentLoader

logger = logging.getLogger(__name__)


class AnalyticQBaseConfig(BaseModel):
    """
    Base configuration class for AnalyticQ backend that load and parses conf file,
    env variables, and allowring access to settings
    """
    settings: Dict[str, Any]

    @classmethod
    def load_config_file(cls, conf_file_path: str , conf_filename: str) -> dict:
        """
        Load a configurarion file and parse into a directory.

        Args:
            conf_file_path: The dir path where the configuration file is located.
            conf_filename: The name of the configuration file.

        Returns:
            dict: A dictionary representing the loaded and parsed configuration data.

        Raises:
            FileNotFoundError: If the configuration file does not exist.
        """
        conf_path = Path(conf_file_path).joinpath(conf_filename)
        if not os.path.exists(conf_path):
            raise FileNotFoundError(f"Config file not found: {conf_path}")
        with open(conf_path, "r") as f:
            return AnalyticQConfigParser.parse(f, str(conf_path))

    @classmethod
    def from_file(cls, conf_filename: str, profile: str = "dev") -> "AnalyticQBaseConfig":
        """
            Load the main configuration for a given profile and a filename, including env
            variables for sensitive data (e.g. API key)

            Args:
                conf_filename: The name of the configuration file to load.
                profile: The profile name (default is "dev")

            Returns:
                AnalyticQBaseConfig: An instance of the conf class with settings loaded settings.

            Raises:
                FileNotFoundException: If the configuration file is not found
                ValueError: If the profile is not found in the configuration file.
        """
        try:
            conf_path_env = str(PathUtil.get_backend_default_config_AnalyticQ_path() / f".env.{profile}")
            AnalyticQEnvironmentLoader.load(conf_path_env, profile)
            if not os.path.exists(conf_filename):
                default_filename = FileUtil.get_default_AnalyticQ_config_filename()
                config_data = cls.load_config_file(PathUtil.get_backend_default_config_AnalyticQ_path(), default_filename)
                config_path = PathUtil.path_to_str(PathUtil.get_config_AnalyticQ_path() / default_filename)
                FileUtil.save_to_json(config_path, config_data)
            else:
                config_data = cls.load_config_file(PathUtil.get_config_AnalyticQ_path(), conf_filename)
            profile_data: dict = config_data.get(profile)
            if not profile_data:
                raise ValueError(f"Profile {profile} not found in config file")

            # Load sensitive data here
            secret_key_env = os.getenv(f"SECRET_KEY_{profile.upper()}")
            if secret_key_env:
                profile_data["secret_key"] = secret_key_env

            cls.settings = profile_data
        except FileNotFoundError as e:
            logger.error(f"{e}")
        except ValueError as e:
            logger.error(f"Error loading config file: {e}")

    @staticmethod
    def get(key: str, default_value: Any = None) -> Any:
        """
        Get a setting value by its key from the loaded settings.

        Args:
            key: Key of setting to retrieve.
            default_value: The default value to return if the key is not found (default is None).

        Returns:
            Any: The value associated with the key, otherwise a default one if the key is not found
        """
        if hasattr(AnalyticQBaseConfig, 'settings'):
            return AnalyticQBaseConfig.settings.get(key, default_value)
        logger.error("Settings are not initialized. Ensure 'from_file' has been called.")
        return default_value
