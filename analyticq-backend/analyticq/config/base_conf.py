import os
import json
import yaml
import logging
from pydantic_settings import BaseSettings
from pydantic import ValidationError
from typing import ClassVar

logger = logging.getLogger(__name__)


class BaseConfig(BaseSettings):
    app_name: ClassVar[str] = "AnalyticQ-Backend"
    debug: bool = False
    secret_key: str

    host: str = "0.0.0.0"
    port: int = 8080
    workers: int = 1

    class Config:
        env_file: str = ".env"
        env_file_encoding: str = "utf-8"

    @classmethod
    def from_file(cls, path: str) -> "BaseConfig":
        if not os.path.exists(path):
            log_message = f"Config file not found: {path}"
            logger.error(log_message)
            raise FileNotFoundError(log_message)
        with open(path, "r") as f:
            if path.endswith(".json"):
                config_data = json.load(f)
            elif path.endswith(".yaml") or path.endswith(".yml"):
                config_data = yaml.safe_load(f)
            else:
                log_message = f"Unsupported config file format: {path}  Use JSON or YAML instead"
                logger.error(log_message)
                raise ValueError(log_message)
        try:
            return cls(**config_data)
        except ValidationError as e:
            log_error = f"Error loading config file: {e}"
            logger.error(log_error)
            raise ValueError(log_error)
