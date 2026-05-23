"""SQLModel ORM models - MySQL tables (monolith shared DB)."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import func
from sqlmodel import Field, SQLModel


class CostCenterTOTVS(SQLModel, table=True):
    __tablename__ = "cost_centers_totvs"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(max_length=25, unique=True)
    name: str = Field(max_length=60)
    classification: str = Field(max_length=60, sa_column_kwargs={"name": "group_name"})


class AssetTypeTOTVS(SQLModel, table=True):
    __tablename__ = "asset_types_totvs"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(max_length=10, unique=True)
    group_code: str = Field(max_length=10, sa_column_kwargs={"name": "group_name"})
    name: str = Field(max_length=40)


class AssetTOTVS(SQLModel, table=True):
    __tablename__ = "assets_totvs"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(max_length=10, unique=True)
    type: str = Field(max_length=100)
    cost_center: str | None = Field(default="", max_length=150)
    active: bool | None = None
    register_number: str | None = Field(default=None, max_length=30)
    description: str | None = Field(default=None, max_length=240)
    supplier: str | None = Field(default=None, max_length=100)
    invoice_number: str | None = Field(default=None, max_length=255)
    assurance_date: datetime | None = None
    observations: str | None = Field(default=None, max_length=999)
    discard_reason: str | None = Field(default=None, max_length=255)
    pattern: str | None = Field(default=None, max_length=255)
    operational_system: str | None = Field(default=None, max_length=255)
    serial_number: str | None = Field(default=None, max_length=255)
    imei: str | None = Field(default=None, max_length=255)
    acquisition_date: datetime | None = None
    value: float | None = None
    depreciation: float | None = None
    ms_office: bool | None = None
    line_number: str | None = Field(default=None, max_length=255)
    operator: str | None = Field(default=None, max_length=255)
    model: str | None = Field(default=None, max_length=255)
    accessories: str | None = Field(default=None, max_length=255)
    unit: str | None = Field(default=None, max_length=3)
    quantity: int | None = None


class MaritalStatusTOTVS(SQLModel, table=True):
    __tablename__ = "marital_status_totvs"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(max_length=1, unique=True)
    description: str = Field(max_length=50)


class GenderTOTVS(SQLModel, table=True):
    __tablename__ = "genders_totvs"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(max_length=1, unique=True)
    description: str = Field(max_length=50)


class NationalityTOTVS(SQLModel, table=True):
    __tablename__ = "nationalities_totvs"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(max_length=3, unique=True)
    description: str = Field(max_length=50)


class EmployeeRoleTOTVS(SQLModel, table=True):
    __tablename__ = "roles_totvs"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(max_length=10, unique=True)
    name: str = Field(max_length=100)


class EducationalLevelTOTVS(SQLModel, table=True):
    __tablename__ = "educational_totvs"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(max_length=3, unique=True)
    description: str = Field(max_length=50)


class EmployeeTOTVS(SQLModel, table=True):
    __tablename__ = "employees_totvs"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    code: str = Field(max_length=10, unique=True)
    full_name: str = Field(max_length=120)
    taxpayer_identification: str = Field(max_length=11, unique=True)
    national_identification: str = Field(max_length=15)
    nationality: str = Field(max_length=50)
    marital_status: str = Field(max_length=50)
    role: str | None = Field(default=None, max_length=100)
    status: str | None = Field(default=None, max_length=100)
    address: str = Field(max_length=255)
    cell_phone: str = Field(max_length=15)
    email: str = Field(max_length=60)
    gender: str = Field(max_length=50)
    birthday: date
    admission_date: date | None = None
    registration: str | None = Field(default=None, max_length=16)
    educational_level: str | None = Field(
        default=None, max_length=50, sa_column_kwargs={"name": "education_level"}
    )


class SyncRecord(SQLModel, table=True):
    __tablename__ = "syncs_totvs"  # type: ignore[assignment]

    id: int | None = Field(default=None, primary_key=True)
    updated_at: datetime | None = Field(
        default=None, sa_column_kwargs={"server_default": func.now()}
    )
    count_new_values: int
    model: str | None = Field(default="", max_length=50)
    execution_time: float
