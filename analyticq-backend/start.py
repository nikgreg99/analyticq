import uvicorn
from analyticq.app import create_app
from analyticq.routes.test_route import router as test_router # noqa

if __name__ == "__main__":

    CONFIG_FILE = None
    ENV_PROFILE = "dev"
    app = create_app(CONFIG_FILE, ENV_PROFILE)
    config = app.state.config
    app.include_router(test_router, prefix="/api/v1")

    uvicorn.run(
        "analyticq.app:create_app",
        host=config.host,
        port=config.port,
        log_level="debug",
        reload=True)
