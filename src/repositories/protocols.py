"""Domain protocols – PEP 695 generics for full decoupling."""

from __future__ import annotations

from typing import Protocol, Sequence, runtime_checkable


# ── Generic type-var (PEP 695) ───────────────────────────────────────

@runtime_checkable
class ReaderRepository[T](Protocol):
    """Read-only repository – typically backed by SQL Server (TOTVS)."""

    async def fetch_all(self) -> Sequence[T]: ...


@runtime_checkable
class WriterRepository[T](Protocol):
    """Read/Write repository – typically backed by MySQL."""

    async def upsert(self, entity: T) -> None: ...

    async def upsert_many(self, entities: Sequence[T]) -> int: ...

    async def get_by_code(self, code: str) -> T | None: ...

    async def get_all_codes(self) -> Sequence[str]: ...

    async def delete_by_code(self, code: str) -> None: ...


@runtime_checkable
class SyncMetadataWriter(Protocol):
    """Persists synchronisation audit records."""

    async def record_sync(
        self, count_new_values: int, execution_time: float, model_name: str
    ) -> None: ...


@runtime_checkable
class ChecksumStore[T](Protocol):
    """Idempotency guard – compare checksums to skip identical rows."""

    def compute(self, entity: T) -> bytes: ...

    async def has_changed(self, entity: T) -> bool: ...
