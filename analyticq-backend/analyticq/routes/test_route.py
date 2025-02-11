from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def endpoint():
    return {"message": "Test endpoint is working!"}
