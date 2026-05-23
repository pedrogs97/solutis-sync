"""ReaderRepository implementations – SQL Server via aioodbc."""

from __future__ import annotations

from datetime import datetime
from typing import Sequence

from loguru import logger

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
from core.database import get_mssql_cursor
from repositories.totvs_queries import (
    SQL_GCCUSTO,
    SQL_IGRUPOPATRIMONIO,
    SQL_IPATRIMONIO,
    SQL_IPATRIMONIO_EXISTS,
    SQL_PCODESTCIVIL,
    SQL_PCODINSTRUCAO,
    SQL_PCODSEXO,
    SQL_PCODNACAO,
    SQL_PFUNCAO,
    SQL_PPESSOA,
)


# ── Helpers ──────────────────────────────────────────────────────────

def _safe(row: dict, key: str, default: str = "") -> str:
    v = row.get(key)
    return str(v).strip() if v is not None else default


def _get_pattern(description: str, pattern: str | None) -> str:
    PATTERN_MAP: dict[str, str] = {
        "001": "PADRÃO STUDIO",
        "002": "PADRÃO ESCRITÓRIO",
    }
    if description and pattern and description.upper().startswith("MACBOOK"):
        return "MACBOOK"
    if pattern and pattern in PATTERN_MAP.values():
        return pattern
    return PATTERN_MAP.get(pattern or "", "")


def _get_accessories(raw: str | None) -> str:
    ACC_MAP: dict[str, str] = {
        "001": "CARREGADOR",
        "002": "FONTE DE ENERGIA",
        "003": "CPU, TECLADO, MOUSE, FONTE DE ENERGIA",
    }
    if not raw:
        return ""
    if raw in ACC_MAP.values():
        return raw
    return ACC_MAP.get(raw, "")


async def _fetch_rows(sql: str) -> list[dict]:
    async with get_mssql_cursor() as cursor:
        await cursor.execute(sql)
        columns: list[str] = [col[0] for col in cursor.description]
        raw = await cursor.fetchall()
        return [dict(zip(columns, row)) for row in raw]


# ── Readers ──────────────────────────────────────────────────────────

class EmployeeReader:
    async def fetch_all(self) -> Sequence[Employee]:
        rows = await _fetch_rows(SQL_PPESSOA)
        results: list[Employee] = []
        for r in rows:
            try:
                city = _safe(r, "CIDADE")
                cep = _safe(r, "CEP")
                street = _safe(r, "RUA")
                num = _safe(r, "NUMERO")
                comp = _safe(r, "COMPLEMENTO")
                bairro = _safe(r, "BAIRRO")
                state = _safe(r, "ESTADO")
                country = _safe(r, "PAIS").replace(":", "").replace(".", "")
                address = f"{street};{num};{comp};{bairro};{city};{state};{country};{cep}"

                bd: datetime | None = r.get("DTNASCIMENTO")
                adm: datetime | None = r.get("ADMISSAO")

                results.append(Employee(
                    code=_safe(r, "CODIGO"),
                    full_name=_safe(r, "NOME"),
                    birthday=bd.date() if bd else None,  # type: ignore[arg-type]
                    taxpayer_identification=_safe(r, "CPF"),
                    national_identification=_safe(r, "CARTIDENTIDADE"),
                    nationality=_safe(r, "NACIONALIDADE"),
                    marital_status=_safe(r, "CIVIL"),
                    role=_safe(r, "CARGO"),
                    status=_safe(r, "SITUACAO") or "Ativo",
                    address=address,
                    cell_phone=_safe(r, "TELEFONE1"),
                    email=_safe(r, "EMAIL"),
                    gender=_safe(r, "SEXO"),
                    admission_date=adm.date() if adm else None,
                    registration=_safe(r, "MATRICULA"),
                    educational_level=_safe(r, "ESCOLARIDADE") or None,
                ))
            except Exception as exc:
                logger.warning("Skipping employee row: {}", exc)
        return results


class MaritalStatusReader:
    async def fetch_all(self) -> Sequence[MaritalStatus]:
        rows = await _fetch_rows(SQL_PCODESTCIVIL)
        return [MaritalStatus(code=_safe(r, "CODINTERNO"), description=_safe(r, "DESCRICAO")) for r in rows]


class GenderReader:
    async def fetch_all(self) -> Sequence[Gender]:
        rows = await _fetch_rows(SQL_PCODSEXO)
        return [Gender(code=_safe(r, "CODINTERNO"), description=_safe(r, "DESCRICAO")) for r in rows]


class NationalityReader:
    async def fetch_all(self) -> Sequence[Nationality]:
        rows = await _fetch_rows(SQL_PCODNACAO)
        return [Nationality(code=_safe(r, "CODINTERNO"), description=_safe(r, "DESCRICAO")) for r in rows]


class EducationalLevelReader:
    async def fetch_all(self) -> Sequence[EducationalLevel]:
        rows = await _fetch_rows(SQL_PCODINSTRUCAO)
        return [EducationalLevel(code=_safe(r, "CODINTERNO"), description=_safe(r, "DESCRICAO")) for r in rows]


class EmployeeRoleReader:
    async def fetch_all(self) -> Sequence[EmployeeRole]:
        rows = await _fetch_rows(SQL_PFUNCAO)
        return [EmployeeRole(code=_safe(r, "CODIGO"), name=_safe(r, "NOME")) for r in rows]


class CostCenterReader:
    async def fetch_all(self) -> Sequence[CostCenter]:
        rows = await _fetch_rows(SQL_GCCUSTO)
        return [
            CostCenter(
                code=_safe(r, "CODREDUZIDO"),
                name=_safe(r, "NOME"),
                classification=_safe(r, "DESCRICAO"),
            )
            for r in rows
        ]


class AssetTypeReader:
    async def fetch_all(self) -> Sequence[AssetType]:
        rows = await _fetch_rows(SQL_IGRUPOPATRIMONIO)
        return [
            AssetType(
                code=str(r["IDGRUPOPATRIMONIO"]) if r.get("IDGRUPOPATRIMONIO") else "",
                group_code=_safe(r, "CODGRUPOPATRIMONIO"),
                name=_safe(r, "DESCRICAO"),
            )
            for r in rows
        ]


class AssetReader:
    async def fetch_all(self) -> Sequence[Asset]:
        rows = await _fetch_rows(SQL_IPATRIMONIO)
        results: list[Asset] = []
        for r in rows:
            try:
                acq: datetime | None = r.get("DATAAQUISICAO")
                grt: datetime | None = r.get("GARANTIA")
                results.append(Asset(
                    code=str(r["IDPATRIMONIO"]) if r.get("IDPATRIMONIO") else "",
                    type=_safe(r, "TIPO"),
                    cost_center=_safe(r, "CENTROCUSTO") or None,
                    active=r.get("ATIVO") is not None and r.get("ATIVO") == 1,
                    register_number=_safe(r, "PATRIMONIO"),
                    description=_safe(r, "DESCRICAO"),
                    supplier=_safe(r, "FORNECEDOR"),
                    invoice_number=_safe(r, "NOTA"),
                    assurance_date=grt,
                    observations=_safe(r, "OBSERVACOES"),
                    pattern=_get_pattern(_safe(r, "DESCRICAO"), r.get("PADRAOEQUIP01")),
                    operational_system=_safe(r, "SISTEMAOPERACIONAL"),
                    serial_number=_safe(r, "SERIE"),
                    imei=_safe(r, "IMEI") or _safe(r, "IMEI02"),
                    acquisition_date=acq,
                    value=float(str(r.get("VALORBASE", 0)).replace(",", ".")) if r.get("VALORBASE") else 0.0,
                    ms_office=r.get("PACOTEOFFICE") == "SIM",
                    line_number=_safe(r, "LINHA"),
                    operator=_safe(r, "OPERADORA01"),
                    accessories=_get_accessories(r.get("ACESSORIOS01")),
                    quantity=int(r["QUANTIDADE"]) if r.get("QUANTIDADE") else 0,
                    unit=_safe(r, "UNIDADE"),
                    depreciation=float(str(r.get("DEPRECIACAO", 0)).replace(",", ".")) if r.get("DEPRECIACAO") else 0.0,
                ))
            except Exception as exc:
                logger.warning("Skipping asset row: {}", exc)
        return results


class AssetExistenceChecker:
    """Checks whether an asset still exists in TOTVS."""

    async def exists(self, code: str) -> bool:
        async with get_mssql_cursor() as cursor:
            await cursor.execute(SQL_IPATRIMONIO_EXISTS, (code,))
            row = await cursor.fetchone()
            return row is not None
