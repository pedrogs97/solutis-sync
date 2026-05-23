"""APScheduler async scheduler - triggers sync jobs on a cron schedule."""

from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from api.deps import build_delete_orphan_use_case, build_sync_use_case
from core.config import get_settings

_settings = get_settings()
scheduler = AsyncIOScheduler()


async def _run_full_sync() -> None:
    logger.info("⏰ Scheduled sync triggered")
    use_case = build_sync_use_case()
    await use_case.execute()

    delete_uc = build_delete_orphan_use_case()
    await delete_uc.execute()
    logger.info("⏰ Scheduled sync finished")


def configure_scheduler() -> AsyncIOScheduler:
    scheduler.add_job(
        _run_full_sync,
        trigger="cron",
        hour=_settings.sync_cron_hour,
        minute=_settings.sync_cron_minute,
        id="totvs_full_sync",
        replace_existing=True,
        max_instances=1,
    )
    return scheduler
