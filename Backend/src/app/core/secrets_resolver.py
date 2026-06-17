"""Secrets bootstrap — P9 file vault + P10 AWS / HashiCorp Vault.

Loads secrets into ``os.environ`` at startup. Values already set in the
environment are never overwritten.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _merge_into_environ(pairs: dict[str, Any], *, source: str) -> dict[str, str]:
    applied: dict[str, str] = {}
    for key, value in pairs.items():
        if not isinstance(key, str):
            continue
        env_key = key.upper().replace(".", "_")
        if env_key in os.environ and os.environ[env_key]:
            continue
        os.environ[env_key] = str(value)
        applied[env_key] = str(value)
    if applied:
        logger.info("Secrets %s loaded %s keys", source, len(applied))
    return applied


def load_vault_into_environ() -> dict[str, str]:
    """Merge JSON vault file from ``SECRETS_VAULT_FILE``."""

    path = (os.getenv("SECRETS_VAULT_FILE") or "").strip()
    if not path:
        return {}
    file_path = Path(path)
    if not file_path.is_file():
        logger.warning("SECRETS_VAULT_FILE not found: %s", path)
        return {}

    try:
        raw = json.loads(file_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Could not read secrets vault: %s", exc)
        return {}

    if not isinstance(raw, dict):
        logger.warning("Secrets vault must be a JSON object")
        return {}

    return _merge_into_environ(raw, source="vault-file")


def load_aws_secrets_into_environ() -> dict[str, str]:
    """Fetch JSON secret from AWS Secrets Manager when configured."""

    secret_id = (
        os.getenv("SECRETS_AWS_SECRET_ARN")
        or os.getenv("SECRETS_AWS_SECRET_ID")
        or ""
    ).strip()
    if not secret_id:
        return {}

    try:
        import boto3  # type: ignore[import-untyped]
    except ImportError:
        logger.warning(
            "SECRETS_AWS_SECRET_* set but boto3 not installed; "
            "pip install 'fast-accounts-backend[secrets-aws]'"
        )
        return {}

    region = (os.getenv("SECRETS_AWS_REGION") or "us-east-1").strip()
    try:
        client = boto3.client("secretsmanager", region_name=region)
        response = client.get_secret_value(SecretId=secret_id)
    except Exception as exc:
        logger.warning("AWS Secrets Manager fetch failed: %s", exc)
        return {}

    payload = response.get("SecretString") or ""
    if not payload:
        return {}
    try:
        raw = json.loads(payload)
    except json.JSONDecodeError:
        logger.warning("AWS secret is not JSON; expected key/value object")
        return {}
    if not isinstance(raw, dict):
        return {}
    return _merge_into_environ(raw, source="aws-sm")


def load_hashicorp_vault_into_environ() -> dict[str, str]:
    """Read KV v2 secret from HashiCorp Vault via HTTP API."""

    addr = (os.getenv("VAULT_ADDR") or "").strip().rstrip("/")
    token = (os.getenv("VAULT_TOKEN") or "").strip()
    secret_path = (os.getenv("VAULT_SECRET_PATH") or "").strip().lstrip("/")
    if not addr or not token or not secret_path:
        return {}

    import httpx

    url = f"{addr}/v1/{secret_path}"
    try:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(url, headers={"X-Vault-Token": token})
            resp.raise_for_status()
            body = resp.json()
    except Exception as exc:
        logger.warning("HashiCorp Vault fetch failed: %s", exc)
        return {}

    data = body.get("data", {})
    if isinstance(data.get("data"), dict):
        raw = data["data"]
    elif isinstance(data, dict):
        raw = data
    else:
        return {}
    return _merge_into_environ(raw, source="hashicorp-vault")


def bootstrap_secrets() -> dict[str, str]:
    """Load all configured secret providers (file → AWS → Vault)."""

    applied: dict[str, str] = {}
    applied.update(load_vault_into_environ())
    applied.update(load_aws_secrets_into_environ())
    applied.update(load_hashicorp_vault_into_environ())
    return applied


def get_secret(name: str, *, default: str = "") -> str:
    """Read secret from environment (after bootstrap)."""

    return (os.getenv(name) or default).strip()
