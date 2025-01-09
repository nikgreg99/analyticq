from typing import Optional
from fastapi import FastAPI
from .config import get_backend_config
from .config.base_conf import BaseConfig
from .config.logging_conf import logging_init

from analyticq.routes.test_route import router as test_router


def create_app(config_file: Optional[str] = None, env_profile: str = "dev") -> FastAPI:

    if config_file:
        config = BaseConfig.from_file(config_file)
    else:
        config = get_backend_config(env_profile)

    # Init logging backend
    logging_init()
    app = FastAPI(
        debug=config.debug,
        title=config.app_name,
        extra=config)
    app.state.config = config
    app.include_router(test_router, prefix="/api/v1")
    return app
