"""Async database engines and session factories."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import aioodbc  # type: ignore[import-untyped]
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession as SQLModelAsyncSession

from core.config import get_settings

_settings = get_settings()

# ── MySQL async engine (read/write) ──────────────────────────────────

mysql_engine = create_async_engine(
    _settings.mysql_dsn,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)


async def init_mysql_tables() -> None:
    """Create tables that do not exist yet."""
    async with mysql_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


@asynccontextmanager
async def get_mysql_session() -> AsyncGenerator[SQLModelAsyncSession]:
    async with SQLModelAsyncSession(mysql_engine, expire_on_commit=False) as session:
        yield session


# ── SQL Server async connection (read-only via aioodbc) ──────────────


@asynccontextmanager
async def get_mssql_connection() -> AsyncGenerator[aioodbc.Connection]:
    conn = await aioodbc.connect(dsn=_settings.mssql_dsn, autocommit=True)
    try:
        yield conn
    finally:
        await conn.close()


@asynccontextmanager
async def get_mssql_cursor() -> AsyncGenerator[aioodbc.Cursor]:
    async with get_mssql_connection() as conn:
        cursor = await conn.cursor()
        try:
            yield cursor
        finally:
            await cursor.close()
