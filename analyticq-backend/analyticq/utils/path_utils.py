import logging
from pathlib import Path

from .const import AnalytiCQConfigConst

logger = logging.getLogger(__name__)


def get_default_analyticq_config_filename(config_file_format: str = AnalytiCQConfigConst.JSON_EXTENSION) -> str:
    if config_file_format == AnalytiCQConfigConst.JSON_EXTENSION:
        return f"{AnalytiCQConfigConst.DEFAULT_ANALYTICQ_CONFIG_FILE}.{AnalytiCQConfigConst.JSON_EXTENSION}"
    elif config_file_format == AnalytiCQConfigConst.YAML_EXTENSION:
        return f"{AnalytiCQConfigConst.DEFAULT_ANALYTICQ_CONFIG_FILE}.{AnalytiCQConfigConst.YAML_EXTENSION}"
    else:
        return f"{AnalytiCQConfigConst.DEFAULT_ANALYTICQ_CONFIG_FILE}.{AnalytiCQConfigConst.YML_EXTENSION}"


def path_to_str(path_obj: Path) -> str:
    return str(path_obj)


def get_os_home_path() -> Path:
    return Path.home()


def get_home_analyticq_path() -> Path:
    return get_os_home_path() / AnalytiCQConfigConst.ANALYTICQ_BASE_DIR


def get_config_analyticq_path() -> Path:
    return get_home_analyticq_path() / AnalytiCQConfigConst.ANALYTICQ_CONFIG_FOLDER


def get_backend_default_config_path() -> Path:
    return Path.cwd() / AnalytiCQConfigConst.ANALYTICQ_CONFIG_FOLDER


def get_backend_default_test_path() -> Path:
    return Path.cwd() / AnalytiCQConfigConst.ANALYTICQ_TEST_FILE_FOLDER


def get_codebase_repos_path() -> Path:
    return get_home_analyticq_path() / AnalytiCQConfigConst.ANALYTICQ_REPOS_FOLDER


def get_codebase_script_path() -> Path:
    return get_home_analyticq_path() / AnalytiCQConfigConst.ANALYTICQ_SCRIPTS_FOLDER


def get_codebase_repos_path_str() -> str:
    codebase_repo_path = get_codebase_repos_path()
    return path_to_str(codebase_repo_path)


def get_codebase_script_path_str() -> str:
    codebase_script_path = get_codebase_script_path()
    return path_to_str(codebase_script_path)


def create_folder_if_not_exists(folder_path: Path) -> bool:
    if not folder_path.exists():
        try:
            folder_path.mkdir(exist_ok=True)
        except Exception:
            logger.error(f"Failed to create folder at given location: {path_to_str(folder_path)}...")
        return True
    return False
