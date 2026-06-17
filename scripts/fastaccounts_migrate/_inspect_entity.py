#!/usr/bin/env python3
"""Inspect user/company and membership for a given id."""
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

TARGET = sys.argv[1] if len(sys.argv) > 1 else "cmpfm1nn40000lhq3xfbnw96y"


async def main() -> None:
    db = Prisma()
    await db.connect()
    tid = TARGET
    company = await db.company.find_unique(where={"id": tid})
    user = await db.user.find_unique(where={"id": tid})
    print(f"Target: {tid}")
    if company:
        print(f"  AS COMPANY: {company.name!r} slug={getattr(company, 'slug', None)}")
        n = await db.customer.count(where={"companyId": tid})
        print(f"  customers={n} invoices={await db.salesinvoice.count(where={'companyId': tid})}")
    else:
        print("  AS COMPANY: not found")
    if user:
        print(f"  AS USER: email={user.email!r} name={user.firstName} {user.lastName}")
        mems = await db.companymembership.find_many(where={"userId": tid}, include={"company": True})
        for m in mems:
            c = m.company
            print(f"    membership company={c.id} {c.name!r} role={m.roleId}")
    else:
        print("  AS USER: not found")
    # all users and companies summary
    print("\nAll companies:")
    for c in await db.company.find_many():
        print(f"  {c.id} {c.name!r} cust={await db.customer.count(where={'companyId': c.id})}")
    print("\nAll users:")
    for u in await db.user.find_many():
        mems = await db.companymembership.find_many(where={"userId": u.id})
        print(f"  {u.id} {u.email!r} memberships={len(mems)}")
    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
