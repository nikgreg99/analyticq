from analyticq.routes.test_route import router as test_router
from analyticq.util import (create_folder_if_not_exists,
                            get_codebase_repositories_folder_path,
                            get_codebase_scripts_folder_path,
                            get_home_analyticq_path)
from fastapi import FastAPI

from .config.base_conf import AnalyticQBaseConfig
from .config.logger_conf import logging_init


def create_analyticq_root_folder():
    create_folder_if_not_exists(get_home_analyticq_path())
    create_folder_if_not_exists(get_codebase_repositories_folder_path())
    create_folder_if_not_exists(get_codebase_scripts_folder_path())


def init_analtytiq_backend_context():
    create_analyticq_root_folder()


def create_app(config_file: str, env_profile: str = "dev") -> FastAPI:
    init_analtytiq_backend_context()
    AnalyticQBaseConfig.from_file(config_file, env_profile)
    # Init logging backend
    logging_init()
    print(AnalyticQBaseConfig.get("app_name"))
    app = FastAPI(
        title=AnalyticQBaseConfig.get("app_name"),
        debug=AnalyticQBaseConfig.get("debug"),
    )
    app.include_router(test_router, prefix="/api/v1")
    return app
