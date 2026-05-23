"""Application use-case - removes assets that no longer exist in TOTVS."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from loguru import logger

from repositories.protocols import WriterRepository
from schemas.entities import Asset


class DeleteOrphanAssetsUseCase:
    """For each asset stored in MySQL, verify if it still exists in TOTVS.

    If not, delete from MySQL (both the ``assets_totvs`` mirror table).
    """

    def __init__(
        self,
        asset_writer: WriterRepository[Asset],
        existence_checker: AssetExistenceCheckerProtocol,
    ) -> None:
        self._writer = asset_writer
        self._checker = existence_checker

    async def execute(self) -> int:
        logger.info("[delete_orphan_assets] START")
        codes = await self._writer.get_all_codes()
        deleted = 0
        for code in codes:
            if not await self._checker.exists(code):
                await self._writer.delete_by_code(code)
                logger.info("[delete_orphan_assets] Deleted code={}", code)
                deleted += 1

        match deleted:
            case 0:
                logger.info("[delete_orphan_assets] No orphans found")
            case 1:
                logger.info("[delete_orphan_assets] 1 orphan deleted")
            case n:
                logger.info("[delete_orphan_assets] {} orphans deleted", n)

        return deleted


# ── Protocol for existence check (dependency inversion) ──────────


@runtime_checkable
class AssetExistenceCheckerProtocol(Protocol):
    async def exists(self, code: str) -> bool: ...
