import json
from pathlib import Path
from threading import Lock
from typing import Dict, Optional

from analyticq.utils import get_home_analyticq_path


class ConfigCodebaseManager():

    _instance = None
    _lock = Lock()

    def _new_(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super.__new__(cls)
        return cls._instance

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            default_path = get_home_analyticq_path()
            default_path.mkdir(exist_ok=True)
            self.config_path = Path(config_path) if config_path else default_path / "codebase_manager_config.json"
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        if self.config_path.exists():
            with open(self.config_path, "r") as conf_file:
                return json.load(conf_file)
        else:
            default_config = {
                "base_dir": str(self.config_path),
                "default_branch": "main",
                "retention_days": 15
            }
            self._save_config(default_config)
            return default_config

    def _save_config(self, config: Dict):
        with open(config["base_dir"], "w") as conf_file:
            json.dump(config, conf_file, indent=4)

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return self.config.get(key, default)

    def set(self, key: str, value: str):
        self.config[key] = value
        self._save_config(self.config)
