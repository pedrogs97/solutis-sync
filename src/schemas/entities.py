"""Domain entities - pure data, no ORM dependency."""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class _Base(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore", frozen=True)


# ── Lookup / reference entities ──────────────────────────────────────


class CostCenter(_Base):
    code: str
    name: str
    classification: str


class AssetType(_Base):
    code: str
    group_code: str
    name: str


class MaritalStatus(_Base):
    code: str
    description: str


class Gender(_Base):
    code: str
    description: str


class Nationality(_Base):
    code: str
    description: str


class EmployeeRole(_Base):
    code: str
    name: str


class EducationalLevel(_Base):
    code: str
    description: str


# ── Core entities ────────────────────────────────────────────────────


class Employee(_Base):
    code: str
    full_name: str
    birthday: date
    taxpayer_identification: str
    national_identification: str
    nationality: str
    marital_status: str
    role: str
    status: str = "Ativo"
    address: str
    cell_phone: str
    email: str
    gender: str
    admission_date: date | None = None
    registration: str
    educational_level: str | None = None


class Asset(_Base):
    code: str
    type: str
    cost_center: str | None = None
    active: bool
    register_number: str
    description: str
    supplier: str
    invoice_number: str
    assurance_date: datetime | None = None
    observations: str
    discard_reason: str = ""
    pattern: str
    operational_system: str
    serial_number: str
    imei: str
    acquisition_date: datetime | None = None
    value: float
    ms_office: bool
    line_number: str
    operator: str
    model: str = ""
    accessories: str
    unit: str
    quantity: int
    depreciation: float


# ── Sync metadata ────────────────────────────────────────────────────


class SyncRecord(_Base):
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore", frozen=False)
    count_new_values: int
    execution_time: float
    model: str = "employee"
