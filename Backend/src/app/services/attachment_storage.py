"""Local filesystem blob store for attachments (dev/single-node).

When ``ATTACHMENT_S3_BUCKET`` is set, uploads use S3-compatible storage instead.
"""

from __future__ import annotations

import os
import re
import uuid
from pathlib import Path

from app.core.config import get_settings

_SAFE_NAME = re.compile(r"[^a-zA-Z0-9._-]+")


class UnsafeStorageKeyError(ValueError):
    """A storage key that would escape the uploads root or the company subtree."""


def assert_safe_storage_key(storage_key: str, *, company_id: str | None = None) -> str:
    """Validate a (possibly client-supplied) storage key; return the normalized key.

    Blocks the attachment path-traversal LFI: a registered key like
    ``../../../../etc/passwd`` (or another tenant's ``otherCompany/...``) must never
    resolve outside the caller's own uploads subtree.
    """

    key = (storage_key or "").strip().replace("\\", "/").lstrip("/")
    if not key:
        raise UnsafeStorageKeyError("empty storage key")
    parts = key.split("/")
    if any(p in ("", ".", "..") for p in parts):
        raise UnsafeStorageKeyError(f"unsafe storage key: {storage_key!r}")
    if len(key) >= 2 and key[1] == ":":  # Windows drive-letter absolute path
        raise UnsafeStorageKeyError(f"absolute storage key rejected: {storage_key!r}")
    if company_id is not None and parts[0] != company_id:
        raise UnsafeStorageKeyError("storage key is outside the company scope")
    return key


def _s3_enabled() -> bool:
    return bool(get_settings().attachment_s3_bucket.strip())


def uploads_root() -> Path:
    root = Path(get_settings().attachment_upload_dir or "uploads")
    if not root.is_absolute():
        root = Path(__file__).resolve().parents[3] / root
    return root


def company_upload_dir(company_id: str) -> Path:
    path = uploads_root() / company_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def _save_upload_s3(*, company_id: str, file_name: str, data: bytes) -> tuple[str, str]:
    """S3-compatible upload (requires boto3 and env bucket config)."""

    try:
        import boto3
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("boto3 required for S3 attachment storage") from exc

    settings = get_settings()
    safe = _SAFE_NAME.sub("_", file_name.strip()) or "file"
    storage_key = f"{company_id}/{uuid.uuid4().hex}_{safe}"
    client_kwargs: dict[str, object] = {"region_name": settings.attachment_s3_region}
    if settings.attachment_s3_endpoint:
        client_kwargs["endpoint_url"] = settings.attachment_s3_endpoint
    if settings.attachment_s3_access_key:
        client_kwargs["aws_access_key_id"] = settings.attachment_s3_access_key
        client_kwargs["aws_secret_access_key"] = settings.attachment_s3_secret_key
    client = boto3.client("s3", **client_kwargs)
    client.put_object(
        Bucket=settings.attachment_s3_bucket,
        Key=storage_key,
        Body=data,
    )
    return storage_key, f"s3://{settings.attachment_s3_bucket}/{storage_key}"


def save_upload(*, company_id: str, file_name: str, data: bytes) -> tuple[str, str]:
    """Return ``(storage_key, absolute_path_or_uri)``."""

    if _s3_enabled():
        return _save_upload_s3(company_id=company_id, file_name=file_name, data=data)

    safe = _SAFE_NAME.sub("_", file_name.strip()) or "file"
    storage_key = f"{company_id}/{uuid.uuid4().hex}_{safe}"
    dest = uploads_root() / storage_key
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return storage_key, str(dest)


def resolve_path(storage_key: str, *, company_id: str | None = None) -> Path:
    key = (storage_key or "").strip()
    if key.startswith("s3://"):
        raise FileNotFoundError(
            f"S3-backed attachment {storage_key!r}; download via signed URL in production"
        )

    safe_key = assert_safe_storage_key(key, company_id=company_id)
    root = uploads_root().resolve()
    candidate = (root / safe_key).resolve()
    # Defense in depth: even a validated key must never resolve outside the root.
    if not candidate.is_relative_to(root):
        raise UnsafeStorageKeyError(f"storage key escapes uploads root: {storage_key!r}")

    if _s3_enabled():
        # Local dev fallback: blobs may still exist on disk from pre-S3 uploads.
        if candidate.is_file():
            return candidate
        raise FileNotFoundError(
            f"S3-backed attachment {storage_key!r}; download via signed URL in production"
        )
    return candidate

