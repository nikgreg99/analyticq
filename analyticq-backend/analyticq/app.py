from analyticq.routes.test_route import router as test_router
from analyticq.utils import (create_folder_if_not_exists,
                             get_codebase_repos_path, get_codebase_script_path,
                             get_home_analyticq_path)
from fastapi import FastAPI

from .config.base_conf import AnalyticQBaseConfig
from .config.logger_conf import logging_init


def create_analyticq_root_folder():
    create_folder_if_not_exists(get_home_analyticq_path())
    create_folder_if_not_exists(get_codebase_repos_path())
    create_folder_if_not_exists(get_codebase_script_path())


def init_analtytiq_backend_context():
    create_analyticq_root_folder()


def create_app(config_file: str, env_profile: str = "dev") -> FastAPI:
    init_analtytiq_backend_context()
    config = AnalyticQBaseConfig.from_file(config_file, env_profile)
    # Init logging backend
    logging_init()
    app = FastAPI(
        debug=config.debug,
        title=config.app_name,
        extra=config)
    app.state.config = config
    app.include_router(test_router, prefix="/api/v1")
    return app
