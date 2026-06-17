"""Persist large report result sets outside Postgres JSON (Phase 2)."""

from __future__ import annotations

import asyncio
import gzip
import json
import logging
from pathlib import Path
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class ReportBlobStore:
    def __init__(self) -> None:
        settings = get_settings()
        self._base = Path(settings.report_storage_dir or "report_exports")
        self._base.mkdir(parents=True, exist_ok=True)
        self._s3_bucket = (settings.report_s3_bucket or "").strip()
        self._s3_configured = bool(
            self._s3_bucket
            and (settings.report_s3_access_key or "").strip()
            and (settings.report_s3_secret_key or "").strip()
        )

    def _local_path(self, storage_key: str) -> Path:
        return self._base / storage_key

    def _object_key(self, company_id: str, run_id: str) -> str:
        return f"{company_id}/{run_id}.json.gz"

    async def save_rows(
        self,
        *,
        company_id: str,
        run_id: str,
        rows: list[dict[str, Any]],
    ) -> str:
        storage_key = self._object_key(company_id, run_id)
        payload = gzip.compress(
            json.dumps(rows, default=str).encode("utf-8"),
            compresslevel=6,
        )
        if self._s3_configured:
            await asyncio.to_thread(self._upload_s3_sync, storage_key, payload)
        path = self._local_path(storage_key)
        path.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(path.write_bytes, payload)
        return storage_key

    async def load_rows(self, *, storage_key: str) -> list[dict[str, Any]]:
        if self._s3_configured:
            try:
                data = await asyncio.to_thread(self._download_s3_sync, storage_key)
                return json.loads(gzip.decompress(data).decode("utf-8"))
            except Exception:  # noqa: BLE001
                logger.warning("S3 load failed for %s, trying local", storage_key)
        path = self._local_path(storage_key)
        if not path.is_file():
            return []
        raw = await asyncio.to_thread(path.read_bytes)
        data = json.loads(gzip.decompress(raw).decode("utf-8"))
        return data if isinstance(data, list) else []

    def _upload_s3_sync(self, key: str, body: bytes) -> None:
        settings = get_settings()
        import boto3

        client_kwargs: dict[str, Any] = {
            "region_name": settings.report_s3_region or "us-east-1",
        }
        endpoint = (settings.report_s3_endpoint or "").strip()
        if endpoint:
            client_kwargs["endpoint_url"] = endpoint
        client = boto3.client(
            "s3",
            aws_access_key_id=settings.report_s3_access_key,
            aws_secret_access_key=settings.report_s3_secret_key,
            **client_kwargs,
        )
        client.put_object(
            Bucket=self._s3_bucket, Key=key, Body=body, ContentType="application/gzip"
        )

    def _download_s3_sync(self, key: str) -> bytes:
        settings = get_settings()
        import boto3

        client_kwargs: dict[str, Any] = {
            "region_name": settings.report_s3_region or "us-east-1",
        }
        endpoint = (settings.report_s3_endpoint or "").strip()
        if endpoint:
            client_kwargs["endpoint_url"] = endpoint
        client = boto3.client(
            "s3",
            aws_access_key_id=settings.report_s3_access_key,
            aws_secret_access_key=settings.report_s3_secret_key,
            **client_kwargs,
        )
        resp = client.get_object(Bucket=self._s3_bucket, Key=key)
        return resp["Body"].read()


_blob_store: ReportBlobStore | None = None


def get_report_blob_store() -> ReportBlobStore:
    global _blob_store
    if _blob_store is None:
        _blob_store = ReportBlobStore()
    return _blob_store
