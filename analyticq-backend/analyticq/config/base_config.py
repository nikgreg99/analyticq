import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

from analyticq.util import FileUtil, PathUtil
from pydantic import BaseModel

from .config_parser import AnalyticQConfigParser
from .env_loader import AnalyticQEnvironmentLoader

logger = logging.getLogger(__name__)


class AnalyticQBaseConfig(BaseModel):
    """
    Base configuration class for AnalyticQ backend that loads and parses config files
    and environment variables, allowing access to settings.
    """

    # Private class-level config storage
    _settings: Optional[Dict[str, Any]] = None

    @classmethod
    def load_config_file(cls, conf_file_path: str, conf_filename: str) -> Dict[str, Any]:
        """
        Load and parse a configuration file.

        Raises:
            FileNotFoundError: If the config file does not exist.
        """
        conf_path = Path(conf_file_path) / conf_filename
        if not conf_path.exists():
            raise FileNotFoundError(f"Config file not found: {conf_path}")
        with open(conf_path, "r") as f:
            return AnalyticQConfigParser.parse(f, str(conf_path))

    @classmethod
    def from_file(cls, conf_filename: str, profile: str = "dev") -> None:
        """
        Initialize the class-level config from file and env variables.
        """
        try:
            # Load env vars unless inside Docker
            env_path = PathUtil.get_backend_default_config_AnalyticQ_path() / f".env.{profile}"
            if os.getenv("RUNNING_IN_DOCKER", "false").lower() != "true":
                AnalyticQEnvironmentLoader.load(str(env_path), profile)

            config_dir = PathUtil.get_config_AnalyticQ_path()
            full_conf_path = Path(conf_filename)

            if not full_conf_path.exists():
                default_filename = FileUtil.get_default_AnalyticQ_config_filename()
                config_data = cls.load_config_file(
                    PathUtil.get_backend_default_config_AnalyticQ_path(),
                    default_filename
                )
                FileUtil.save_to_json(str(config_dir / default_filename), config_data)
            else:
                config_data = cls.load_config_file(config_dir, conf_filename)

            profile_data = config_data.get(profile)
            if not profile_data:
                raise ValueError(f"Profile '{profile}' not found in configuration.")

            # Inject secrets
            secret_key = os.getenv(f"SECRET_KEY_{profile.upper()}")
            if secret_key:
                profile_data["secret_key"] = secret_key

            cls._settings = profile_data

        except (FileNotFoundError, ValueError) as e:
            logger.error(f"Failed to load configuration: {e}")
            raise

    @staticmethod
    def get(key: str, default_value: Any = None) -> Any:
        """
        Static method to retrieve config values.

        Returns:
            The setting value if available, else default_value.
        """
        if AnalyticQBaseConfig._settings is not None:
            return AnalyticQBaseConfig._settings.get(key, default_value)
        logger.error("Configuration not initialized. Call `from_file()` before accessing settings.")
        return default_value
