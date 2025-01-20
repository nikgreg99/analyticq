from fastapi import APIRouter

router = APIRouter()


@router.get("/test")
def endpoint():
    return {"message": "Test endpoint is working!"}
