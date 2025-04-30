import uvicorn
from analyticq.app import create_app
from analyticq.config import AnalyticQBaseConfig
from watchfiles import run_process


def run_backend():
    """
    Initializes and runs the FastAPI backend server using uvicorn.

    The function creates a FastAPI application with the specified configuration file
    and runs it using uvicorn ASGI server with the settings defined in AnalyticQBaseConfig.

    Returns:
        None

    Raises:
        ConfigError: If configuration parameters are invalid or missing
        UvicornError: If server fails to start properly
    """
    app = create_app("analyticq_backend_config.json", "dev")

    uvicorn.run(
        app=app,
        host=AnalyticQBaseConfig.get("host"),
        port=AnalyticQBaseConfig.get("port"),
        log_level=AnalyticQBaseConfig.get("debug"),
        lifespan="on",
        loop="asyncio")


if __name__ == "__main__":
    run_process(".", target=run_backend, args=(), kwargs={})
