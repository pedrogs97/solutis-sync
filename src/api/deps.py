"""Dependency injection – wires readers, writers, and use-cases together."""

from __future__ import annotations

from services.delete_orphan_assets import DeleteOrphanAssetsUseCase
from services.sync_use_case import SyncUseCase
from repositories.mysql_writers import (
    AssetTypeWriter,
    AssetWriter,
    CostCenterWriter,
    EducationalLevelWriter,
    EmployeeRoleWriter,
    EmployeeWriter,
    GenderWriter,
    MaritalStatusWriter,
    NationalityWriter,
    SyncMetadataWriterImpl,
)
from repositories.totvs_readers import (
    AssetExistenceChecker,
    AssetReader,
    AssetTypeReader,
    CostCenterReader,
    EducationalLevelReader,
    EmployeeReader,
    EmployeeRoleReader,
    GenderReader,
    MaritalStatusReader,
    NationalityReader,
)


def build_sync_use_case() -> SyncUseCase:
    return SyncUseCase(
        # readers (TOTVS – SQL Server)
        employee_reader=EmployeeReader(),
        marital_status_reader=MaritalStatusReader(),
        gender_reader=GenderReader(),
        nationality_reader=NationalityReader(),
        educational_level_reader=EducationalLevelReader(),
        role_reader=EmployeeRoleReader(),
        cost_center_reader=CostCenterReader(),
        asset_type_reader=AssetTypeReader(),
        asset_reader=AssetReader(),
        # writers (MySQL)
        employee_writer=EmployeeWriter(),
        marital_status_writer=MaritalStatusWriter(),
        gender_writer=GenderWriter(),
        nationality_writer=NationalityWriter(),
        educational_level_writer=EducationalLevelWriter(),
        role_writer=EmployeeRoleWriter(),
        cost_center_writer=CostCenterWriter(),
        asset_type_writer=AssetTypeWriter(),
        asset_writer=AssetWriter(),
        # metadata
        sync_metadata=SyncMetadataWriterImpl(),
    )


def build_delete_orphan_use_case() -> DeleteOrphanAssetsUseCase:
    return DeleteOrphanAssetsUseCase(
        asset_writer=AssetWriter(),
        existence_checker=AssetExistenceChecker(),
    )
