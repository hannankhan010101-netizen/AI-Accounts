#!/usr/bin/env python3
"""Pre-deploy checks: env, DB, Smart Settings posting defaults for tenant."""
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

from prisma_generated import Prisma

MIGRATE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(MIGRATE_DIR))
from _tenant import tenant_id  # noqa: E402

CID = tenant_id()

DEFAULT_KEYS = (
    "receivablesNominalCode",
    "payablesNominalCode",
    "salesNominalCode",
    "purchasesNominalCode",
)


async def main() -> int:
    issues: list[str] = []

    if not os.getenv("DATABASE_URL"):
        issues.append("DATABASE_URL not set")
    if not os.getenv("JWT_SECRET_KEY") or len(os.getenv("JWT_SECRET_KEY", "")) < 16:
        issues.append("JWT_SECRET_KEY missing or too short")

    db = Prisma()
    await db.connect()

    company = await db.company.find_unique(where={"id": CID})
    if company is None:
        issues.append(f"Company {CID} not found")

    smart = await db.smartsettings.find_unique(where={"companyId": CID})
    payload = smart.payload if smart and isinstance(smart.payload, dict) else {}
    defaults = payload.get("defaults") if isinstance(payload.get("defaults"), dict) else {}

    missing_defaults = [k for k in DEFAULT_KEYS if not defaults.get(k)]
    if missing_defaults:
        issues.append(f"Smart Settings defaults missing: {', '.join(missing_defaults)}")

    bank_count = await db.bankaccount.count(where={"companyId": CID})
    if bank_count == 0:
        issues.append("No bank accounts for tenant")

    banks_without_nominal = await db.bankaccount.count(
        where={"companyId": CID, "nominalCode": None}
    )
    if banks_without_nominal:
        issues.append(f"{banks_without_nominal} bank account(s) without nominalCode")

    await db.disconnect()

    print(f"=== Pre-flight deploy ({CID}) ===\n")
    print(f"  DATABASE_URL: {'set' if os.getenv('DATABASE_URL') else 'MISSING'}")
    print(f"  DIRECT_URL:   {'set' if os.getenv('DIRECT_URL') else '(optional)'}")
    for key in DEFAULT_KEYS:
        val = defaults.get(key) if smart else None
        print(f"  defaults.{key}: {val or '(missing)'}")
    print(f"  Bank accounts: {bank_count}")

    if issues:
        print("\n  PREFLIGHT: FAIL")
        for item in issues:
            print(f"    - {item}")
        return 1

    print("\n  PREFLIGHT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
