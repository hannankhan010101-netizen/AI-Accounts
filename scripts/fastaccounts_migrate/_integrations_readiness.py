#!/usr/bin/env python3
"""Print integration env readiness and tenant FBR queue counts."""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "Backend"
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv

load_dotenv(ROOT / ".env")
if os.getenv("DIRECT_URL"):
    os.environ["DATABASE_URL"] = os.environ["DIRECT_URL"]

from app.core.config import get_settings
from app.repositories.fbr_repository import FbrRepository
from app.services.integrations_readiness_service import build_integrations_readiness
from prisma_generated import Prisma

MIGRATE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MIGRATE_DIR))
from _tenant import tenant_id  # noqa: E402

CID = tenant_id()


async def main() -> int:
    settings = get_settings()
    db = Prisma()
    await db.connect()
    repo = FbrRepository(db)
    errors = await repo.list_errors(company_id=CID)
    due = await repo.list_due_retries(company_id=CID)
    await db.disconnect()

    r = build_integrations_readiness(
        settings,
        fbr_error_count=len(errors),
        fbr_due_retry_count=len(due),
    )

    print(f"=== Integrations readiness ({CID}) ===\n")
    for key in ("fbr", "paypro", "kuickpay"):
        p = r[key]
        print(
            f"  {key:8} enabled={p['enabled']!s:5}  configured={p['configured']!s:5}  "
            f"ready={p['ready']!s:5}"
        )
    print(f"\n  FBR errors in DB:     {r['fbr']['errorCount']}")
    print(f"  FBR due retries:      {r['fbr']['dueRetryCount']}")
    print(f"  FBR retry worker flag: {r['fbrRetryWorker']}")

    any_ready = r["fbr"]["ready"] or r["paypro"]["ready"] or r["kuickpay"]["ready"]
    if any_ready:
        print("\n  INTEGRATIONS: at least one provider configured")
        return 0
    print("\n  INTEGRATIONS: not configured (OK for go-live without FBR/PayPro)")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
