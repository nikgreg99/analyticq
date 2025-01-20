import logging
from pathlib import Path

from .const import AnalyticQConst

logger = logging.getLogger(__name__)


def get_default_AnalyticQ_config_filename(config_file_format: str = AnalyticQConst.JSON_EXTENSION) -> str:
    extensions = {
        AnalyticQConst.JSON_EXTENSION: f"{AnalyticQConst.DEFAULT_ANALYTICQ_CONFIG_FILE}.{AnalyticQConst.JSON_EXTENSION}",
        AnalyticQConst.YAML_EXTENSION: f"{AnalyticQConst.DEFAULT_ANALYTICQ_CONFIG_FILE}.{AnalyticQConst.YAML_EXTENSION}",
    }
    return extensions.get(config_file_format, f"{AnalyticQConst.DEFAULT_ANALYTICQ_CONFIG_FILE}.{AnalyticQConst.YML_EXTENSION}")


def path_to_str(path_obj: Path) -> str:
    return str(path_obj)


def get_path_as_str(path_func: callable):
    return str(path_func())


def get_os_home_path() -> Path:
    return Path.home()


def get_current_cwd_path() -> Path:
    return Path.cwd()


def get_last_dir_name(file_path: Path) -> str:
    return file_path.name


def get_home_AnalyticQ_path() -> Path:
    return get_os_home_path() / AnalyticQConst.ANALYTICQ_BASE_DIR


def get_config_AnalyticQ_path() -> Path:
    return get_home_AnalyticQ_path() / AnalyticQConst.ANALYTICQ_CONFIG_FOLDER


def get_backend_default_config_AnalyticQ_path() -> Path:
    return get_current_cwd_path() / AnalyticQConst.ANALYTICQ_CONFIG_FOLDER


def get_backend_default_test_AnalyticQ_path() -> Path:
    return get_current_cwd_path() / AnalyticQConst.ANALYTICQ_TEST_FILE_FOLDER


def get_codebase_repositories_folder_AnalyticQ_path() -> Path:
    return get_home_AnalyticQ_path() / AnalyticQConst.ANALYTICQ_REPOS_FOLDER


def get_codebase_scripts_folder_AnalyticQ_path() -> Path:
    return get_home_AnalyticQ_path() / AnalyticQConst.ANALYTICQ_SCRIPTS_FOLDER


def get_codebase_repositories_folder_path_AnalyticQ_str() -> str:
    codebase_repo_path = get_codebase_repositories_folder_AnalyticQ_path()
    return path_to_str(codebase_repo_path)


def get_codebase_scripts_folder_path_AnalyticQ_str() -> str:
    codebase_script_path = get_codebase_scripts_folder_AnalyticQ_path()
    return path_to_str(codebase_script_path)


async def create_folder_if_not_exists_async(folder_path: Path) -> bool:
    try:
        if not folder_path.exists():
            folder_path.mkdir(exist_ok=True, parents=True)
            logger.info(f"Folder created at {path_to_str(folder_path)}")
            return True
    except (FileNotFoundError, PermissionError, OSError) as e:
        logger.error(f"Error while creating folder at {folder_path}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error while creating folder at {folder_path}: {e}")
    return False
