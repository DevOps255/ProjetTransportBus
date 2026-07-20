from fastapi import APIRouter

router = APIRouter(prefix='topics', tags=['topics'])

@router.get("/ping")
def ping():
    return {
        "features": "topics",
        "status": "alive"
    }