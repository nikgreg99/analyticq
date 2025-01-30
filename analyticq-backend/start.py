import uvicorn
from analyticq.app import create_app
from analyticq.config import AnalyticQBaseConfig
from analyticq.routes.test_route import router as test_router  # noqa

if __name__ == "__main__":

    app = create_app("analyticq_backend_config.json", "dev")
    app.include_router(test_router, prefix="/api/v1")

    uvicorn.run(
        "analyticq.app:create_app",
        host=AnalyticQBaseConfig.get("host"),
        port=AnalyticQBaseConfig.get("port"),
        log_level=AnalyticQBaseConfig.get("debug"),
        lifespan="on",
        factory=True,
        reload=True)
