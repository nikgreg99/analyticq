import json
import logging
import os
from typing import Optional

import yaml
from analyticq.utils import get_backend_config_path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class AnalyticqBaseConfig(BaseSettings):
    app_name: str
    debug: bool
    host: str
    port: int
    workers: int
    secret_key: str

    class Config:
        env_file: Optional[str] = None  # Dynamically set during runtime
        env_file_encoding: str = "utf-8"

    @classmethod
    def load_environment(cls, profile: str) -> None:
        conf_path_env = str(get_backend_config_path() / f".env.{profile}")
        if os.path.exists(conf_path_env):
            load_dotenv(conf_path_env)
            logger.info(f"Loaded {profile} profile...")
        else:
            logger.warning(f".env file for profile {profile} was not found at: {conf_path_env}")

    @classmethod
    def load_config_file(cls, conf_filename: str) -> dict:
        conf_path = str(get_backend_config_path() / conf_filename)
        if not os.path.exists(conf_path):
            log_message = f"Config file not found: {conf_path}"
            raise FileNotFoundError(log_message)
        with open(conf_path, "r") as f:
            if conf_path.endswith(".json"):
                return json.load(f)
            elif conf_path.endswith(".yaml") or conf_path.endswith(".yml"):
                return yaml.safe_load(f)
            else:
                log_message = f"Unsupported config file format: {conf_path}  Use JSON or YAML instead"
                raise ValueError(log_message)

    @classmethod
    def from_file(cls, conf_filename: str, profile: str = "dev") -> "AnalyticqBaseConfig":
        try:
            cls.load_environment(profile)
            config_data = cls.load_config_file(conf_filename)
            profile_data = config_data.get(profile)

            if not profile_data:
                raise ValueError(f"Profile {profile} not found in config file")

            # Load sensitive data here
            secret_key_env = os.getenv(f"SECRET_KEY_{profile.upper()}")
            if secret_key_env:
                profile_data["secret_key"] = secret_key_env
            return cls(**profile_data)
        except FileNotFoundError as e:
            logger.error(f"{e}")
        except ValueError as e:
            logger.error(f"lError loading config file: {e}")
