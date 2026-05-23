"""solutis-sync - FastAPI application entrypoint."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from api.routes import router as api_router
from core.config import get_settings
from core.database import init_mysql_tables
from core.scheduler import configure_scheduler

_settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    logger.info("🚀 {} starting …", _settings.app_name)
    await init_mysql_tables()

    _scheduler = configure_scheduler()
    _scheduler.start()
    logger.info(
        "📅 Scheduler running - cron {}:{:02d}",
        _settings.sync_cron_hour,
        _settings.sync_cron_minute,
    )

    yield

    _scheduler.shutdown(wait=False)
    logger.info("🛑 {} stopped", _settings.app_name)


app = FastAPI(
    title=_settings.app_name,
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(api_router)
