from fastapi import APIRouter

from config import settings

router = APIRouter(tags=["System"])


@router.get("/health")
async def health_check() -> dict:
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
