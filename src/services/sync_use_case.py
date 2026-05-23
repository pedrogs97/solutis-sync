"""Application use-case - orchestrates the full TOTVS -> MySQL sync."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from time import perf_counter

from loguru import logger

from repositories.protocols import ReaderRepository, SyncMetadataWriter, WriterRepository
from schemas.entities import (
    Asset,
    AssetType,
    CostCenter,
    EducationalLevel,
    Employee,
    EmployeeRole,
    Gender,
    MaritalStatus,
    Nationality,
)


class SyncUseCase:
    """Reads all entities from TOTVS (SQL Server) and upserts into MySQL.

    Uses ``asyncio.TaskGroup`` to run independent syncs concurrently.
    """

    def __init__(
        self,
        # readers (TOTVS)
        employee_reader: ReaderRepository[Employee],
        marital_status_reader: ReaderRepository[MaritalStatus],
        gender_reader: ReaderRepository[Gender],
        nationality_reader: ReaderRepository[Nationality],
        educational_level_reader: ReaderRepository[EducationalLevel],
        role_reader: ReaderRepository[EmployeeRole],
        cost_center_reader: ReaderRepository[CostCenter],
        asset_type_reader: ReaderRepository[AssetType],
        asset_reader: ReaderRepository[Asset],
        # writers (MySQL)
        employee_writer: WriterRepository[Employee],
        marital_status_writer: WriterRepository[MaritalStatus],
        gender_writer: WriterRepository[Gender],
        nationality_writer: WriterRepository[Nationality],
        educational_level_writer: WriterRepository[EducationalLevel],
        role_writer: WriterRepository[EmployeeRole],
        cost_center_writer: WriterRepository[CostCenter],
        asset_type_writer: WriterRepository[AssetType],
        asset_writer: WriterRepository[Asset],
        # metadata
        sync_metadata: SyncMetadataWriter,
    ) -> None:
        self._readers: dict[str, ReaderRepository] = {  # type: ignore[type-arg]
            "marital_status": marital_status_reader,
            "gender": gender_reader,
            "nationality": nationality_reader,
            "educational_level": educational_level_reader,
            "role": role_reader,
            "cost_center": cost_center_reader,
            "asset_type": asset_type_reader,
            "asset": asset_reader,
            "employee": employee_reader,
        }
        self._writers: dict[str, WriterRepository] = {  # type: ignore[type-arg]
            "marital_status": marital_status_writer,
            "gender": gender_writer,
            "nationality": nationality_writer,
            "educational_level": educational_level_writer,
            "role": role_writer,
            "cost_center": cost_center_writer,
            "asset_type": asset_type_writer,
            "asset": asset_writer,
            "employee": employee_writer,
        }
        self._sync_meta = sync_metadata

    # ── public API ────────────────────────────────────────────────────

    async def execute(self) -> dict[str, int]:
        """Run the full synchronisation pipeline. Returns upsert counts."""
        logger.info("─── Sync pipeline START ───")
        results: dict[str, int] = {}

        # Phase 1: lookup tables (concurrent)
        lookup_keys = [
            "marital_status",
            "gender",
            "nationality",
            "educational_level",
            "role",
            "cost_center",
            "asset_type",
        ]

        async with asyncio.TaskGroup() as tg:
            tasks: dict[str, asyncio.Task[int]] = {
                key: tg.create_task(self._sync_entity(key)) for key in lookup_keys
            }

        for key, task in tasks.items():
            results[key] = task.result()

        # Phase 2: core entities (sequential - depend on lookups)
        results["asset"] = await self._sync_entity("asset")
        results["employee"] = await self._sync_entity("employee")

        logger.info("─── Sync pipeline END ─── results={}", results)
        return results

    # ── private ───────────────────────────────────────────────────────

    async def _sync_entity(self, name: str) -> int:
        start = perf_counter()
        reader = self._readers[name]
        writer = self._writers[name]

        entities: Sequence = await reader.fetch_all()
        count = await writer.upsert_many(entities)

        elapsed = perf_counter() - start
        await self._sync_meta.record_sync(count, elapsed, name)

        match count:
            case 0:
                logger.info("[{}] No changes detected ({:.2f}s)", name, elapsed)
            case 1:
                logger.info("[{}] 1 record upserted ({:.2f}s)", name, elapsed)
            case n:
                logger.info("[{}] {} records upserted ({:.2f}s)", name, n, elapsed)

        return count
