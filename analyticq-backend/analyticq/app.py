from typing import Optional

from analyticq.routes.test_route import router as test_router
from fastapi import FastAPI

from .config.base_conf import AnalyticqBaseConfig
from .config.logger_conf import logging_init


def create_app(config_file: Optional[str] = None, env_profile: str = "dev") -> FastAPI:
    config = AnalyticqBaseConfig.from_file(config_file, env_profile)
    # Init logging backend
    logging_init()
    app = FastAPI(
        debug=config.debug,
        title=config.app_name,
        extra=config)
    app.state.config = config
    app.include_router(test_router, prefix="/api/v1")
    return app
