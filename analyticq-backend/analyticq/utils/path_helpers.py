from pathlib import Path


def get_backend_config_path() -> Path:
    return Path.cwd() / "config"
