import logging
import time
from contextlib import asynccontextmanager
from typing import List

from analyticq.config import CeleryConf, DatabaseConf
from analyticq.config.di import AnalyticQContainer
from analyticq.routes.test_route import router as test_router
from analyticq.util import AnalyticQConst, ImportUtil, PathUtil
from fastapi import FastAPI

import analyticq

from .config.base_conf import AnalyticQBaseConfig
from .config.logger_conf import logging_init

logger = logging.getLogger(__name__)

celery = None


def get_container() -> AnalyticQContainer:
    return AnalyticQContainer()


def get_analyticq_root_structure() -> List[str]:
    return [
        PathUtil.get_home_AnalyticQ_path(),
        PathUtil.get_config_AnalyticQ_path(),
        PathUtil.get_codebase_repositories_AnalyticQ_path(),
        PathUtil.get_codebase_scripts_AnalyticQ_path()
    ]


async def create_AnalyticQ_root_structure():
    required_folders_path: List[str] = get_analyticq_root_structure()
    try:
        for folder_path in required_folders_path:
            await PathUtil.create_folder_if_not_exists_async(folder_path)
            logger.debug(f"Created or verified folder existence at: {folder_path}")
    except Exception as e:
        logger.error(f"Failed to create folder structure: {str(e)}")


@asynccontextmanager
async def backend_context(app: FastAPI):
    global celery
    start_time = time.time()

    container = AnalyticQContainer()
    celery_conf = CeleryConf()

    try:
        db = DatabaseConf()
        await db.init_db()
        await db.run_db_migrations()
        app.state.db = db

        celery = celery_conf.get_celery_app()
        app.state.celery = celery_conf.celery

        logger.info("Init AnalyticQ backend resources...")
        logging_init()
        await create_AnalyticQ_root_structure()

        all_modules = ImportUtil.discover_modules(analyticq)
        container.wire(modules=all_modules)

        app.state.celery.conf.update(celery_conf.settings.model_dump())
        logger.info(f"Analyticq backend started in {time.time() - start_time:2f} seconds")

        yield

    except Exception as e:
        logger.critical(f"Error starting AnalyticQ backend: {str(e)}", exc_info=True)
        raise RuntimeError("Critical error from initizalizing Analyticq backend") from e
    finally:
        # Cleanup resources (dependencies, connection, ecc)
        await app.state.db.close()
        logging.shutdown()
        container.unwire()
        logger.info("Shutdown AnalyticQ backend...")


def create_app(config_file: str = AnalyticQConst.ANALYTICQ_DEFAULT_CONFIG_FILE,
               env_profile: str = AnalyticQConst.ANALYTICQ_DEFAULT_PROFILE) -> FastAPI:
    AnalyticQBaseConfig.from_file(config_file, env_profile)
    app = FastAPI(
        title=AnalyticQBaseConfig.get("app_name"),
        debug=AnalyticQBaseConfig.get("debug"),
        lifespan=backend_context
    )
    app.include_router(test_router, prefix="/api/v1")
    return app
