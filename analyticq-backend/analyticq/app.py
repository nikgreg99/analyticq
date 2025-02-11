import logging
import subprocess
import time
from contextlib import asynccontextmanager
from typing import List

from analyticq.celery_app import get_celery_app
from analyticq.config.di import AnalyticQContainer
from analyticq.manager import AnalyticQDatabaseManager
from analyticq.routes.test_route import router as test_router
from analyticq.util import AnalyticQConst, ImportUtil, PathUtil
from fastapi import FastAPI

import analyticq

from .config.base_conf import AnalyticQBaseConfig
from .config.logger_conf import logging_init

logger = logging.getLogger(__name__)


def check_git_installed() -> None:
    """
    Checks if Git is installed and accessible in the system PATH.

    This function attempts to execute 'git --version' command to verify Git installation.

    Returns:
        None

    Raises:
        RuntimeError: If Git is not installed or not accessible in the system PATH.

    Note:
        This function is essential for repository operations as the application
        requires Git to be properly installed and configured in the system.
    """

    process = subprocess.run(
        ["git", "--version"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True
    )

    if process.returncode != 0:
        logger.critical(
            "Git is not installed or not accessible in system PATH. "
            "Please install Git and ensure it's available in your environment."
        )
        raise RuntimeError("Git installation not found. This application requires Git for repository operations")


def get_container() -> AnalyticQContainer:
    """
    Get the main dependency injection container for AnalyticQ.

    Returns:
        AnalyticQContainer: A new instance of the application's dependency injection container
            that provides access to all configured services and dependencies.
    """
    return AnalyticQContainer()


def get_analyticq_root_structure() -> List[str]:
    """Returns a list of essential AnalyticQ directory paths.

    This function returns the base directory structure required for AnalyticQ to function properly,
    including paths for home directory, configuration, codebase repositories and scripts.

    Returns:
        List[str]: A list containing the following paths:
            - AnalyticQ home directory path
            - AnalyticQ configuration directory path
            - AnalyticQ codebase repositories directory path
            - AnalyticQ codebase scripts directory path
    """
    return [
        PathUtil.get_home_AnalyticQ_path(),
        PathUtil.get_config_AnalyticQ_path(),
        PathUtil.get_codebase_repositories_AnalyticQ_path(),
        PathUtil.get_codebase_scripts_AnalyticQ_path()
    ]


async def create_AnalyticQ_root_structure():
    """
    Creates the root folder structure for AnalyticQ if it doesn't exist.

    This async function creates all required folders for the AnalyticQ application
    by retrieving the folder structure from get_analyticq_root_structure() and
    creating each folder if it doesn't already exist.

    Returns:
        None

    Raises:
        Exception: If there is an error creating any of the folders
    """
    required_folders_path: List[str] = get_analyticq_root_structure()
    try:
        for folder_path in required_folders_path:
            await PathUtil.create_folder_if_not_exists_async(folder_path)
            logger.debug(f"Created or verified folder existence at: {folder_path}")
    except Exception as e:
        logger.error(f"Failed to create folder structure: {str(e)}")
        raise


@asynccontextmanager
async def backend_context(app: FastAPI):
    """
    Initialize and manage the backend context for the AnalyticQ FastAPI application.

    This context manager handles initialization of critical backend resources including:
    - Database connection and migrations
    - Logging configuration
    - Git verification
    - Dependency injection container setup

    Args:
        app (FastAPI): The FastAPI application instance to configure

    Yields:
        None: Yields control back to the application after setup is complete

    Raises:
        RuntimeError: If a critical error occurs during backend initialization
            with the original exception attached as context

    Example:
        async with backend_context(app):
            # Backend resources initialized and available
            ...
        # Resources automatically cleaned up after context exits
    """
    start_time = time.time()

    container = AnalyticQContainer()

    try:
        db = AnalyticQDatabaseManager()
        await db.init_db()
        app.state.db = db

        celery_app = get_celery_app()
        app.state.celery = celery_app

        logger.info("Init AnalyticQ backend resources...")
        logging_init()
        await create_AnalyticQ_root_structure()

        logger.info("Verify Git installation...")
        check_git_installed()

        all_modules = ImportUtil.discover_modules(analyticq)
        container.wire(modules=all_modules)

        logger.info(f"Analyticq backend started in {time.time() - start_time:2f} seconds")

        yield

    except Exception as e:
        logger.critical(f"Error starting AnalyticQ backend: {str(e)}", exc_info=True)
        raise RuntimeError("Critical error from initizalizing Analyticq backend") from e
    finally:
        # Cleanup resources (dependencies, connection, ecc)
        if hasattr(app.state, "db"):
            await app.state.db.close()
        logging.shutdown()
        container.unwire()
        logger.info("Shutdown AnalyticQ backend...")


def create_app(config_file: str = AnalyticQConst.ANALYTICQ_DEFAULT_CONFIG_FILE,
               env_profile: str = AnalyticQConst.ANALYTICQ_DEFAULT_PROFILE) -> FastAPI:
    """
        Creates and configures a FastAPI application instance.
        This function initializes a new FastAPI application with configuration loaded from a specified file.
        It sets up the application with basic settings and includes API routers.
        Args:
                config_file (str): Path to the configuration file. Defaults to AnalyticQConst.ANALYTICQ_DEFAULT_CONFIG_FILE.
                env_profile (str): Environment profile to use. Defaults to AnalyticQConst.ANALYTICQ_DEFAULT_PROFILE.
        Returns:
            FastAPI: Configured FastAPI application instance.
    """
    AnalyticQBaseConfig.from_file(config_file, env_profile)
    app = FastAPI(
        title=AnalyticQBaseConfig.get("app_name"),
        debug=AnalyticQBaseConfig.get("debug"),
        lifespan=backend_context
    )
    app.include_router(test_router)
    return app
