"""Parse role import files (JSON / CSV) — P32."""

from __future__ import annotations

import csv
import json
from io import StringIO
from typing import Any


def parse_role_import_file(*, filename: str, content: bytes) -> list[dict[str, Any]]:
    """Return ``[{name, permissions}, ...]`` from upload bytes.

    Accepts full exports ``{ roles: [...] }``, names-only exports (P44), or CSV.
    """

    name_lower = filename.lower()
    if name_lower.endswith(".json"):
        return _parse_json(content)
    if name_lower.endswith(".csv"):
        return _parse_csv(content)
    raise ValueError("Unsupported file type; use .json or .csv")


def _parse_json(content: bytes) -> list[dict[str, Any]]:
    try:
        data = json.loads(content.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid JSON file") from exc
    if isinstance(data, dict) and isinstance(data.get("roles"), list):
        rows = data["roles"]
    elif isinstance(data, list):
        rows = data
    else:
        raise ValueError("JSON must be { \"roles\": [...] } or a role array")
    return [_normalize_row(r, index=i) for i, r in enumerate(rows)]


def _parse_csv(content: bytes) -> list[dict[str, Any]]:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("CSV must be UTF-8") from exc
    reader = csv.DictReader(StringIO(text))
    if not reader.fieldnames:
        raise ValueError("CSV header row required")
    fields = {f.lower().strip(): f for f in reader.fieldnames if f}
    name_key = fields.get("name")
    perms_key = fields.get("permissions") or fields.get("permission")
    if not name_key:
        raise ValueError("CSV must include a 'name' column")
    out: list[dict[str, Any]] = []
    for i, row in enumerate(reader):
        name = (row.get(name_key) or "").strip()
        perms_raw = (row.get(perms_key) or "").strip() if perms_key else ""
        permissions = _split_permissions(perms_raw)
        out.append(_normalize_row({"name": name, "permissions": permissions}, index=i))
    return out


def _split_permissions(raw: str) -> list[str]:
    if not raw:
        return []
    if raw.startswith("["):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return [str(p).strip() for p in parsed if str(p).strip()]
        except json.JSONDecodeError:
            pass
    for sep in ("|", ";"):
        if sep in raw:
            return [p.strip() for p in raw.split(sep) if p.strip()]
    return [p.strip() for p in raw.split(",") if p.strip()]


def _normalize_row(row: Any, *, index: int) -> dict[str, Any]:
    if not isinstance(row, dict):
        raise ValueError(f"Row {index + 1}: expected an object")
    name = str(row.get("name", "")).strip()
    if not name:
        raise ValueError(f"Row {index + 1}: name is required")
    perms_raw = row.get("permissions", [])
    if isinstance(perms_raw, str):
        permissions = _split_permissions(perms_raw)
    elif isinstance(perms_raw, list):
        permissions = [str(p).strip() for p in perms_raw if str(p).strip()]
    else:
        permissions = []
    return {"name": name, "permissions": permissions}


def describe_role_import_file(*, filename: str, content: bytes) -> dict[str, Any]:
    """Hints for import preview UI (P46)."""

    name_lower = filename.lower()
    if not name_lower.endswith(".json"):
        return {"namesOnly": False, "fileFormat": "csv"}
    try:
        data = json.loads(content.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {"namesOnly": False, "fileFormat": "json"}
    names_only = bool(isinstance(data, dict) and data.get("namesOnly"))
    rows: list[Any] = []
    if isinstance(data, dict) and isinstance(data.get("roles"), list):
        rows = data["roles"]
    elif isinstance(data, list):
        rows = data
    if rows and all(
        isinstance(r, dict) and str(r.get("name", "")).strip() and not r.get("id")
        for r in rows
    ):
        names_only = True
    return {"namesOnly": names_only, "fileFormat": "json"}
