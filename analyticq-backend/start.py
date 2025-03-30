import uvicorn
from analyticq.app import create_app
from analyticq.config import AnalyticQBaseConfig

if __name__ == "__main__":

    app = create_app("analyticq_backend_config.json", "dev")

    uvicorn.run(
        app=app,
        host=AnalyticQBaseConfig.get("host"),
        port=AnalyticQBaseConfig.get("port"),
        log_level=AnalyticQBaseConfig.get("debug"),
        lifespan="on",
        loop="asyncio")
