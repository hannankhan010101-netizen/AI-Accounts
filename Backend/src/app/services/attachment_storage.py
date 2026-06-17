"""Local filesystem blob store for attachments (dev/single-node)."""

from __future__ import annotations

import re
import uuid
from pathlib import Path

from app.core.config import get_settings

_SAFE_NAME = re.compile(r"[^a-zA-Z0-9._-]+")


def uploads_root() -> Path:
    root = Path(get_settings().attachment_upload_dir or "uploads")
    if not root.is_absolute():
        root = Path(__file__).resolve().parents[3] / root
    return root


def company_upload_dir(company_id: str) -> Path:
    path = uploads_root() / company_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_upload(*, company_id: str, file_name: str, data: bytes) -> tuple[str, str]:
    """Return ``(storage_key, absolute_path)``."""

    safe = _SAFE_NAME.sub("_", file_name.strip()) or "file"
    storage_key = f"{company_id}/{uuid.uuid4().hex}_{safe}"
    dest = uploads_root() / storage_key
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return storage_key, str(dest)


def resolve_path(storage_key: str) -> Path:
    return uploads_root() / storage_key
