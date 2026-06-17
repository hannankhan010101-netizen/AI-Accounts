"""Shared tenant id for go-live / migration verification scripts."""
from __future__ import annotations

import os

NAFY_PHARMA_TENANT_ID = "cmpfm1nst0001lhq3rz09938z"


def tenant_id() -> str:
    """Company id under test — override with GO_LIVE_COMPANY_ID or PREFLIGHT_COMPANY_ID."""

    return (
        os.getenv("GO_LIVE_COMPANY_ID")
        or os.getenv("PREFLIGHT_COMPANY_ID")
        or NAFY_PHARMA_TENANT_ID
    )
