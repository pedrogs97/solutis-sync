"""Application settings - loaded from environment / .env file."""

from __future__ import annotations

import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings - loaded from environment / .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # ── MySQL ─────────────────────────────────────────────
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_database: str = "solutis"

    # ── SQL Server 17 (TOTVS - read-only) ────────────────────────────
    mssql_dsn: str = (
        "DRIVER={ODBC Driver 17 for SQL Server};SERVER=127.0.0.1;DATABASE=totvs;UID=sa;PWD=sa"
    )

    # ── Scheduler ────────────────────────────────────────────────────
    sync_cron_hour: str = "3"
    sync_cron_minute: int = 0
    sync_cron_week: str = ""

    # ── App ──────────────────────────────────────────────────────────
    app_name: str = "solutis-sync"
    log_level: str = "INFO"
    base_dir: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    @property
    def mysql_dsn(self) -> str:
        return (
            f"mysql+aiomysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
