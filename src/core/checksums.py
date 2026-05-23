"""Checksum utility - deterministic JSON serialisation."""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel


def _default(obj: Any) -> str:
    match obj:
        case datetime():
            return obj.isoformat()
        case date():
            return obj.isoformat()
        case _:
            return str(obj)


def compute_checksum(entity: BaseModel) -> bytes:
    """Return a stable SHA-256 digest for any Pydantic model."""
    payload = json.dumps(entity.model_dump(), sort_keys=True, indent=2, default=_default).encode(
        "utf-8"
    )
    return hashlib.sha256(payload).digest()
