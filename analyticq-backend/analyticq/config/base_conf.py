import json
import logging
import os
from typing import Any, Dict

import yaml
from analyticq.util import (get_backend_default_config_path,
                            get_config_analyticq_path,
                            get_default_analyticq_config_filename, path_to_str)
from dotenv import load_dotenv
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class AnalyticQBaseConfig(BaseModel):
    settings: Dict[str, Any]

    @staticmethod
    def __parse_config_file(file, conf_path: str):
        SUPPORTED_FORMATS = {"json": json.load, "yaml": yaml.safe_load, "yml": yaml.safe_load}
        ext = conf_path.rsplit(".", 1)[-1]
        if ext in SUPPORTED_FORMATS:
            return SUPPORTED_FORMATS[ext](file)

    @classmethod
    def load_environment(cls, profile: str) -> None:
        conf_path_env = str(get_backend_default_config_path() / f".env.{profile}")
        if os.path.exists(conf_path_env):
            load_dotenv(conf_path_env)
            logger.info(f"Loaded {profile} profile...")
        else:
            logger.warning(f".env file for profile {profile} was not found at: {conf_path_env}")

    @classmethod
    def load_config_file(cls, conf_file_path, conf_filename: str) -> dict:
        conf_path = str(conf_file_path / conf_filename)
        if not os.path.exists(conf_path):
            raise FileNotFoundError(f"Config file not found: {conf_path}")
        with open(conf_path, "r") as f:
            return cls.__parse_config_file(f, conf_path)

    @classmethod
    def from_file(cls, conf_filename: str = None, profile: str = "dev") -> "AnalyticQBaseConfig":
        try:
            cls.load_environment(profile)
            if conf_filename is None or not os.path.exists(conf_filename):
                default_filename = get_default_analyticq_config_filename()
                config_data = cls.load_config_file(get_backend_default_config_path(), default_filename)
                config_path = path_to_str(get_config_analyticq_path() / get_default_analyticq_config_filename())
                cls.save_to_json(config_path, config_data)
            else:
                config_data = cls.load_config_file(get_config_analyticq_path(), conf_filename)
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

    @classmethod
    def save_to_json(cls, conf_file_path: str, config_data: dict):
        try:
            with open(conf_file_path, "w") as conf_file:
                json.dump(config_data, conf_file , indent=4)
        except Exception:
            logger.error("Error saving  configuration")
            return None

    @staticmethod
    def get(key: str, default_value: Any = None) -> Any:
        if hasattr(AnalyticQBaseConfig, 'settings'):
            return AnalyticQBaseConfig.settings.get(key, default_value)
        logger.error("Settings are not initialized. Ensure 'from_file' has been called.")
        return default_value
