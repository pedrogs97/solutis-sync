"""FastAPI routes/endpoints for the sync service."""

from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse
from loguru import logger

from api.deps import build_delete_orphan_use_case, build_sync_use_case
from core.config import get_settings

_settings = get_settings()

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": _settings.app_name}


@router.post("/fetch-totvs", tags=["Sync"])
async def force_fetch_totvs(background_tasks: BackgroundTasks) -> JSONResponse:
    """Triggers a full TOTVS sync as a background task."""

    async def _bg_sync() -> None:
        uc = build_sync_use_case()
        await uc.execute()
        delete_uc = build_delete_orphan_use_case()
        await delete_uc.execute()

    background_tasks.add_task(_bg_sync)
    logger.info("Manual sync triggered via /fetch-totvs")
    return JSONResponse(content={"message": "Sync task enqueued"})
