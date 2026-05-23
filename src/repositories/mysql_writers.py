"""WriterRepository implementations - MySQL via SQLModel async."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

from loguru import logger
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlmodel import SQLModel, select

from core.checksums import compute_checksum
from core.database import get_mysql_session
from models.mysql_models import (
    AssetTOTVS,
    AssetTypeTOTVS,
    CostCenterTOTVS,
    EducationalLevelTOTVS,
    EmployeeRoleTOTVS,
    EmployeeTOTVS,
    GenderTOTVS,
    MaritalStatusTOTVS,
    NationalityTOTVS,
    SyncRecord,
)
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

T = TypeVar("T", bound=BaseModel)
_ORM = TypeVar("_ORM", bound=SQLModel)


class _GenericMySQLWriter[Entity: BaseModel, ORM: SQLModel]:
    """Generic upsert writer with checksum-based idempotency."""

    def __init__(self, orm_cls: type[ORM]) -> None:
        self._orm = orm_cls

    async def get_by_code(self, code: str) -> ORM | None:
        async with get_mysql_session() as session:
            stmt = select(self._orm).where(self._orm.code == code)  # type: ignore[attr-defined]
            result = await session.exec(stmt)
            return result.first()

    async def get_all_codes(self) -> Sequence[str]:
        async with get_mysql_session() as session:
            stmt = select(self._orm.code)  # type: ignore[attr-defined]
            result = await session.exec(stmt)
            return list(result.all())

    async def _has_changed(self, entity: Entity) -> bool:
        existing = await self.get_by_code(entity.code)  # type: ignore[attr-defined]
        if existing is None:
            return True
        existing_dict = {k: v for k, v in existing.model_dump().items() if k != "id"}
        existing_entity = type(entity)(**existing_dict)
        return compute_checksum(entity) != compute_checksum(existing_entity)

    async def upsert(self, entity: Entity) -> None:
        if not await self._has_changed(entity):
            return
        async with get_mysql_session() as session:
            try:
                stmt = select(self._orm).where(
                    self._orm.code == entity.code  # type: ignore[attr-defined]
                )
                result = await session.exec(stmt)
                existing = result.first()
                entity_dict = entity.model_dump()
                if existing:
                    for key, value in entity_dict.items():
                        setattr(existing, key, value)
                    session.add(existing)
                    logger.info("Updated: {} code={}", self._orm.__name__, entity.code)  # type: ignore[attr-defined]
                else:
                    new_record = self._orm(**entity_dict)
                    session.add(new_record)
                    logger.info("Inserted: {} code={}", self._orm.__name__, entity.code)  # type: ignore[attr-defined]
                await session.commit()
            except IntegrityError as exc:
                await session.rollback()
                logger.warning("IntegrityError on {}: {}", self._orm.__name__, exc)
            except Exception as exc:
                await session.rollback()
                logger.error("Error on {}: {}", self._orm.__name__, exc)

    async def upsert_many(self, entities: Sequence[Entity]) -> int:
        count = 0
        for entity in entities:
            await self.upsert(entity)
            count += 1
        return count

    async def delete_by_code(self, code: str) -> None:
        async with get_mysql_session() as session:
            stmt = select(self._orm).where(self._orm.code == code)  # type: ignore[attr-defined]
            result = await session.exec(stmt)
            record = result.first()
            if record:
                await session.delete(record)
                await session.commit()
                logger.info("Deleted: {} code={}", self._orm.__name__, code)


# ── Concrete writers ─────────────────────────────────────────────────


class CostCenterWriter(_GenericMySQLWriter[CostCenter, CostCenterTOTVS]):
    def __init__(self) -> None:
        super().__init__(CostCenterTOTVS)


class AssetTypeWriter(_GenericMySQLWriter[AssetType, AssetTypeTOTVS]):
    def __init__(self) -> None:
        super().__init__(AssetTypeTOTVS)


class AssetWriter(_GenericMySQLWriter[Asset, AssetTOTVS]):
    def __init__(self) -> None:
        super().__init__(AssetTOTVS)


class MaritalStatusWriter(_GenericMySQLWriter[MaritalStatus, MaritalStatusTOTVS]):
    def __init__(self) -> None:
        super().__init__(MaritalStatusTOTVS)


class GenderWriter(_GenericMySQLWriter[Gender, GenderTOTVS]):
    def __init__(self) -> None:
        super().__init__(GenderTOTVS)


class NationalityWriter(_GenericMySQLWriter[Nationality, NationalityTOTVS]):
    def __init__(self) -> None:
        super().__init__(NationalityTOTVS)


class EmployeeRoleWriter(_GenericMySQLWriter[EmployeeRole, EmployeeRoleTOTVS]):
    def __init__(self) -> None:
        super().__init__(EmployeeRoleTOTVS)


class EducationalLevelWriter(_GenericMySQLWriter[EducationalLevel, EducationalLevelTOTVS]):
    def __init__(self) -> None:
        super().__init__(EducationalLevelTOTVS)


class EmployeeWriter(_GenericMySQLWriter[Employee, EmployeeTOTVS]):
    def __init__(self) -> None:
        super().__init__(EmployeeTOTVS)


class SyncMetadataWriterImpl:
    """Persists sync audit rows."""

    async def record_sync(
        self, count_new_values: int, execution_time: float, model_name: str
    ) -> None:
        async with get_mysql_session() as session:
            record = SyncRecord(
                count_new_values=count_new_values,
                execution_time=execution_time,
                model=model_name,
            )
            session.add(record)
            await session.commit()
