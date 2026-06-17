#!/usr/bin/env python3
"""Membership and role details for companies."""
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

USER_ID = "cmpfm1nn40000lhq3xfbnw96y"
DATA_COMPANY = "cmpfl1itj000hqubj7rne8q5f"
USER_COMPANY = "cmpfm1nst0001lhq3rz09938z"


async def main() -> None:
    db = Prisma()
    await db.connect()
    for cid, label in [(DATA_COMPANY, "Nafy-Pharma (data)"), (USER_COMPANY, "HAK (user company)")]:
        c = await db.company.find_unique(where={"id": cid})
        print(f"\n{label}: {c.name if c else 'MISSING'}")
        mems = await db.companymembership.find_many(
            where={"companyId": cid}, include={"user": True, "role": True}
        )
        for m in mems:
            u = m.user
            print(
                f"  member user={u.id} {u.email!r} default={m.isDefault} role={m.role.name if m.role else None}"
            )
        roles = await db.role.find_many(where={"companyId": cid})
        print(f"  roles: {[(r.id, r.name) for r in roles]}")
    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
