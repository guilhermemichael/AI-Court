from fastapi import APIRouter

from app.settings import get_settings

router = APIRouter(tags=["health"])
settings = get_settings()


@router.get("/health")
async def health() -> dict[str, str | bool]:
    return {
        "status": "ok",
        "service": "ai-court-backend",
        "environment": settings.app_env,
        "llm_mode": settings.llm_mode,
        "websocket_ready": True,
    }
