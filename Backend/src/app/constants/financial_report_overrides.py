"""Optional JSON file overrides for Financial report numeric IDs — P18."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.core.config import get_settings

_BUILTIN_FINANCIAL: dict[str, str] = {
    "203": "TB",
    "204": "PNL",
    "205": "BS",
    "207": "FIN_PNL_CAT",
    "208": "FIN_TB12",
    "209": "FIN_CMP",
    "210": "FIN_MTB",
}


def _default_config_path() -> Path:
    return Path(__file__).resolve().parents[3] / "config" / "financial_report_ids.json"


@lru_cache
def financial_live_aliases() -> dict[str, str]:
    """Merge built-in map with optional ``FINANCIAL_REPORT_IDS_FILE`` JSON."""

    merged = dict(_BUILTIN_FINANCIAL)
    settings = get_settings()
    raw_path = (getattr(settings, "financial_report_ids_file", None) or "").strip()
    path = Path(raw_path) if raw_path else _default_config_path()
    if not path.is_file():
        return merged
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return merged
    if not isinstance(data, dict):
        return merged
    for key, value in data.items():
        if str(key).startswith("_"):
            continue
        merged[str(key)] = str(value)
    return merged
