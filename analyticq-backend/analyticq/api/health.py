from fastapi import APIRouter
from fastapi.responses import JSONResponse

health_router = APIRouter()


@health_router.get("/health", tags=["Health"])
async def health_check():
    """
    A simple health check endpoint that returns a 200 OK response.

    Returns:
        JSONResponse: A response with status code 200 and content {'status': 'ok'}
            indicating the service is healthy and running.
    """
    return JSONResponse(status_code=200, content={"status": "ok"})
