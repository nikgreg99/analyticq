import logging
from pathlib import Path

from .const import AnalytiCQConfigConst

logger = logging.getLogger(__name__)


def get_default_analyticq_config_filename(config_file_format: str = AnalytiCQConfigConst.JSON_EXTENSION) -> str:
    extensions = {
        AnalytiCQConfigConst.JSON_EXTENSION: f"{AnalytiCQConfigConst.DEFAULT_ANALYTICQ_CONFIG_FILE}.{AnalytiCQConfigConst.JSON_EXTENSION}",
        AnalytiCQConfigConst.YAML_EXTENSION: f"{AnalytiCQConfigConst.DEFAULT_ANALYTICQ_CONFIG_FILE}.{AnalytiCQConfigConst.YAML_EXTENSION}",
    }
    return extensions.get(config_file_format, f"{AnalytiCQConfigConst.DEFAULT_ANALYTICQ_CONFIG_FILE}.{AnalytiCQConfigConst.YML_EXTENSION}")


def path_to_str(path_obj: Path) -> str:
    return str(path_obj)


def get_path_as_str(path_func: callable):
    return str(path_func())


def get_os_home_path() -> Path:
    return Path.home()


def get_current_cwd_path() -> Path:
    return Path.cwd()


def get_home_analyticq_path() -> Path:
    return get_os_home_path() / AnalytiCQConfigConst.ANALYTICQ_BASE_DIR


def get_config_analyticq_path() -> Path:
    return get_home_analyticq_path() / AnalytiCQConfigConst.ANALYTICQ_CONFIG_FOLDER


def get_backend_default_config_path() -> Path:
    return get_current_cwd_path() / AnalytiCQConfigConst.ANALYTICQ_CONFIG_FOLDER


def get_backend_default_test_path() -> Path:
    return get_current_cwd_path() / AnalytiCQConfigConst.ANALYTICQ_TEST_FILE_FOLDER


def get_codebase_repositories_folder_path() -> Path:
    return get_home_analyticq_path() / AnalytiCQConfigConst.ANALYTICQ_REPOS_FOLDER


def get_codebase_scripts_folder_path() -> Path:
    return get_home_analyticq_path() / AnalytiCQConfigConst.ANALYTICQ_SCRIPTS_FOLDER


def get_codebase_repositories_folder_path_str() -> str:
    codebase_repo_path = get_codebase_repositories_folder_path()
    return path_to_str(codebase_repo_path)


def get_codebase_scripts_folder_path_str() -> str:
    codebase_script_path = get_codebase_scripts_folder_path()
    return path_to_str(codebase_script_path)


def create_folder_if_not_exists(folder_path: Path) -> bool:
    if not folder_path.exists():
        try:
            folder_path.mkdir(exist_ok=True, parents=True)
            logger.info(f"Folder created at {path_to_str(folder_path)}")
            return True
        except FileNotFoundError as e:
            logger.error(
                f"Invalid path specified for folder creation: {path_to_str(folder_path)}. Error: {e}"
            )
        except PermissionError as e:
            logger.error(
                f"Permission denied while creating folder: {path_to_str(folder_path)}. Error: {e}"
            )
        except OSError as e:
            logger.error(
                f"OS error occurred while creating folder: {path_to_str(folder_path)}. Error: {e}"
            )
        except Exception as e:
            logger.error(f"Failed to create folder at given location: {path_to_str(folder_path)}... Error {e}")
        return False
    return False
