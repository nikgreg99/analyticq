import logging
from contextlib import asynccontextmanager
from typing import List

from analyticq.config.di import AnalyticQContainer
from analyticq.routes.test_route import router as test_router
from analyticq.util import AnalyticQConst, PathUtil
from fastapi import FastAPI

from .config.base_conf import AnalyticQBaseConfig
from .config.logger_conf import logging_init

logger = logging.getLogger(__name__)


def get_AnalyticQ_root_structure() -> List[str]:
    return [
        PathUtil.get_home_AnalyticQ_path(),
        PathUtil.get_config_AnalyticQ_path(),
        PathUtil.get_codebase_repositories_AnalyticQ_path(),
        PathUtil.get_codebase_scripts_AnalyticQ_path()
    ]


async def create_AnalayticQ_root_structure():
    required_folders_path: List[str] = get_AnalyticQ_root_structure()
    try:
        for folder_path in required_folders_path:
            await PathUtil.create_folder_if_not_exists_async(folder_path)
            logger.debug(f"Created or verified folder existence at: {folder_path}")
    except Exception as e:
        logger.error(f"Failed to create folder structure: {str(e)}")


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    logging_init()
    logger.info("Iniziatling AnalyticQ backend log service...")
    container = AnalyticQContainer()
    await create_AnalayticQ_root_structure()
    logger.info("Init AnalyticQ backend resources...")
    try:
        container.wire(modules=["analyticq"])
        yield
    finally:
        # Cleanup resources (dependencies, connection, ecc)
        logging.shutdown()
        container.unwire()
        logger.info("Shutdown AnalyticQ backend...")


def create_app(config_file: str = AnalyticQConst.DEFAULT_ANALYTICQ_CONFIG_FILE,
               env_profile: str = AnalyticQConst.DEFAULT_ANALYTICQ_PROFILE) -> FastAPI:
    AnalyticQBaseConfig.from_file(config_file, env_profile)
    app = FastAPI(
        title=AnalyticQBaseConfig.get("app_name"),
        debug=AnalyticQBaseConfig.get("debug"),
        lifespan=app_lifespan
    )
    app.include_router(test_router, prefix="/api/v1")
    return app
