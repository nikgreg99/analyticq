import logging
from pathlib import Path

from .const import AnalyticQConst

logger = logging.getLogger(__name__)


class PathUtil:
    """
    A utility class for file path-related operations.
    """

    @staticmethod
    def path_to_str(path_obj: Path) -> str:
        """
        Convert a Path object to a string.

        Args:
            path_obj (Path): The Path object to convert.

        Returns:
            str: The string representation of the path.
        """
        return str(path_obj)

    @staticmethod
    def get_os_home_path() -> Path:
        """
        Get the user's home directory.

        Returns:
            Path: The user's home directory as a Path object.
        """
        return Path.home()

    @staticmethod
    def get_current_cwd_path() -> Path:
        """
        Get the current working directory.

        Returns:
            Path: The current working directory as a Path object.
        """
        return Path.cwd()

    @staticmethod
    def get_last_dir_name(file_path: Path) -> str:
        """
        Get the last directory name of a given file path.

        Args:
            file_path (Path): The file path to extract the directory name from.

        Returns:
            str: The last directory name.

        Raises:
            ValueError: If the file path is empty.
        """
        dir_name = file_path.name
        if dir_name == "":
            raise ValueError("Path does not contain a directory name.")
        return dir_name

    @staticmethod
    def get_home_AnalyticQ_path() -> Path:
        """
        Get the home directory path for AnalyticQ.

        Returns:
            Path: The home directory path for AnalyticQ.
        """
        return PathUtil.get_os_home_path().joinpath(AnalyticQConst.ANALYTICQ_BASE_DIR)

    @staticmethod
    def get_config_AnalyticQ_path() -> Path:
        """
        Get the configuration directory path for AnalyticQ.

        Returns:
            Path: The configuration directory path for AnalyticQ.
        """
        return PathUtil.get_home_AnalyticQ_path().joinpath(AnalyticQConst.ANALYTICQ_CONFIG_FOLDER)

    @staticmethod
    def get_backend_AnalyticQ_path() -> Path:
        """
        Returns the path to the backend AnalyticQ root folder.


        Returns:
            Path: Absolute path to the backend AnalyticQ root folder
        """
        return PathUtil.get_current_cwd_path().joinpath(AnalyticQConst.ANALYTICQ_BACKEND_FOLDER)

    @staticmethod
    def get_backend_default_config_AnalyticQ_path() -> Path:
        """
        Get the backend default configuration directory path for AnalyticQ.

        Returns:
            Path: The backend default configuration directory path for AnalyticQ.
        """
        return PathUtil.get_current_cwd_path().joinpath(AnalyticQConst.ANALYTICQ_CONFIG_FOLDER)

    @staticmethod
    def get_backend_default_test_AnalyticQ_path() -> Path:
        """
        Get the default test path for the AnalyticQ backend.

        Returns:
            Path: The path to the default test folder for the AnalyticQ backend.
        """
        return PathUtil.get_backend_AnalyticQ_path().joinpath(AnalyticQConst.ANALYTICQ_TEST_FOLDER)

    @staticmethod
    def get_backend_default_test_file_AnalyticQ_path() -> Path:
        """
        Get the backend default test files directory path for AnalyticQ.

        Returns:
            Path: The backend default test files directory path for AnalyticQ.
        """
        return PathUtil.get_backend_default_test_AnalyticQ_path().joinpath(AnalyticQConst.ANALYTICQ_TEST_FILE_FOLDER)

    @staticmethod
    def get_codebase_repositories_AnalyticQ_path() -> Path:
        """
        Get the codebase repositories directory path for AnalyticQ.

        Returns:
            Path: The codebase repositories directory path for AnalyticQ.
        """
        return PathUtil.get_home_AnalyticQ_path().joinpath(AnalyticQConst.ANALYTICQ_REPOS_FOLDER)

    @staticmethod
    def get_codebase_scripts_AnalyticQ_path() -> Path:
        """
        Get the codebase scripts directory path for AnalyticQ.

        Returns:
            Path: The codebase scripts directory path for AnalyticQ.
        """
        return PathUtil.get_home_AnalyticQ_path().joinpath(AnalyticQConst.ANALYTICQ_SCRIPTS_FOLDER)

    @staticmethod
    def get_codebase_repositories_path_AnalyticQ_str() -> str:
        """
        Get the codebase repositories directory path as a string for AnalyticQ.

        Returns:
            str: The codebase repositories directory path as a string.
        """
        codebase_repo_path = PathUtil.get_codebase_repositories_AnalyticQ_path()
        return PathUtil.path_to_str(codebase_repo_path)

    @staticmethod
    def get_codebase_scripts_path_AnalyticQ_str() -> str:
        """
        Get the codebase scripts directory path as a string for AnalyticQ.

        Returns:
            str: The codebase scripts directory path as a string.
        """
        codebase_script_path = PathUtil.get_codebase_scripts_AnalyticQ_path()
        return PathUtil.path_to_str(codebase_script_path)

    @staticmethod
    async def create_folder_if_not_exists_async(folder_path: Path) -> bool:
        """
        Create a folder if it does not already exist.

        Args:
            folder_path (Path): The folder path to create.

        Returns:
            bool: True if the folder was created, False if it already exists.
        """
        try:
            if not folder_path.exists():
                folder_path.mkdir(exist_ok=True, parents=True)
                logger.info(f"Folder created at {PathUtil.path_to_str(folder_path)}")
                return True
        except (FileNotFoundError, PermissionError, OSError) as e:
            logger.error(f"Error while creating folder at {folder_path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while creating folder at {folder_path}: {e}")
        return False
