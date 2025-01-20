import logging
from contextlib import asynccontextmanager
from typing import List

from analyticq.routes.test_route import router as test_router
from analyticq.util import (AnalyticQConst, create_folder_if_not_exists_async,
                            get_codebase_repositories_folder_AnalyticQ_path,
                            get_codebase_scripts_folder_AnalyticQ_path,
                            get_config_AnalyticQ_path, get_home_AnalyticQ_path)
from fastapi import FastAPI

from .config.base_conf import AnalyticQBaseConfig
from .config.logger_conf import logging_init

logger = logging.getLogger(__name__)


async def create_AnalayticQ_root_structure():
    required_folders_path: List[str] = [  # Listing dir should be respected
        get_home_AnalyticQ_path(),
        get_config_AnalyticQ_path(),
        get_codebase_repositories_folder_AnalyticQ_path(),
        get_codebase_scripts_folder_AnalyticQ_path()
    ]
    try:
        for folder_path in required_folders_path:
            await create_folder_if_not_exists_async(folder_path)
            logger.debug(f"Created or verified folder existence at: {folder_path}")
    except Exception as e:
        logger.error(f"Failed to create folder structure: {str(e)}")


async def init_AnalyticQ_backend_context():
    # Init logging first
    logging_init()
    logger.info("Iniziatling AnalyticQ backend....")

    # Here define init context
    await create_AnalayticQ_root_structure()


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    await init_AnalyticQ_backend_context()
    logger.info("Init AnalyticQ backend...")
    try:
        yield
    finally:
        logging.shutdown()
        logger.info("Shutdown AnalyticQ backend...")


def create_app(config_file: str = AnalyticQConst.DEFAULT_ANALYTICQ_CONFIG_FILE, env_profile: str = AnalyticQConst.DEFAULT_ANALYTICQ_PROFILE) -> FastAPI:
    AnalyticQBaseConfig.from_file(config_file, env_profile)
    app = FastAPI(
        title=AnalyticQBaseConfig.get("app_name"),
        debug=AnalyticQBaseConfig.get("debug"),
        lifespan=app_lifespan
    )
    app.include_router(test_router, prefix="/api/v1")
    return app
