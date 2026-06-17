#!/usr/bin/env python3
"""
Associate migrated FastAccounts data with a user.

Modes:
  link (default) — grant user admin membership on the data company + set as default login.
  move           — reassign all transactional/master rows to the user's default company.

Usage:
  python _associate_user_data.py --user-id cmpfm1nn40000lhq3xfbnw96y
  python _associate_user_data.py --user-id ... --mode move
"""
from __future__ import annotations

import argparse
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

DATA_COMPANY_ID = "cmpfl1itj000hqubj7rne8q5f"  # Nafy-Pharma (migrated data)

# Singleton config tables: one row per company — delete target stub before merge.
SINGLETON_TABLES = (
    "business_information",
    "smart_settings",
    "lock_date_settings",
    "taxes_year_end_config",
)

# Never reassign these (tenant structure, not transactional data).
SKIP_TABLES = frozenset(
    {
        "company_memberships",
        "roles",
        "Company",  # Prisma model maps to "Company" — check actual table name
    }
)


async def tables_with_company_id(db: Prisma) -> list[str]:
    rows = await db.query_raw(
        """
        SELECT c.table_name
        FROM information_schema.columns c
        JOIN information_schema.tables t
          ON t.table_name = c.table_name AND t.table_schema = c.table_schema
        WHERE c.table_schema = 'public'
          AND c.column_name = 'company_id'
          AND t.table_type = 'BASE TABLE'
        ORDER BY c.table_name
        """
    )
    return [r["table_name"] for r in rows if r["table_name"] not in SKIP_TABLES]


async def count_for(db: Prisma, table: str, company_id: str) -> int:
    rows = await db.query_raw(
        f'SELECT COUNT(*)::int AS n FROM "{table}" WHERE company_id = $1',
        company_id,
    )
    return int(rows[0]["n"])


async def user_default_company(db: Prisma, user_id: str) -> tuple[str, str]:
    user = await db.user.find_unique(where={"id": user_id})
    if not user:
        raise SystemExit(f"User not found: {user_id}")
    mems = await db.companymembership.find_many(
        where={"userId": user_id}, include={"company": True}
    )
    if not mems:
        raise SystemExit(f"User has no company memberships: {user_id}")
    default = next((m for m in mems if m.isDefault), mems[0])
    return default.companyId, default.company.name


async def admin_role_id(db: Prisma, company_id: str) -> str:
    roles = await db.role.find_many(where={"companyId": company_id})
    if not roles:
        raise SystemExit(f"No roles for company {company_id}")
    admin = next((r for r in roles if r.name.lower() == "administrator"), roles[0])
    return admin.id


async def mode_link(db: Prisma, user_id: str, data_company_id: str) -> None:
    role_id = await admin_role_id(db, data_company_id)
    existing = await db.companymembership.find_unique(
        where={"companyId_userId": {"companyId": data_company_id, "userId": user_id}}
    )
    if existing:
        await db.companymembership.update(
            where={"id": existing.id},
            data={"roleId": role_id, "isDefault": True},
        )
        print(f"Updated existing membership on data company (default=True)")
    else:
        await db.companymembership.create(
            data={
                "companyId": data_company_id,
                "userId": user_id,
                "roleId": role_id,
                "isDefault": True,
            }
        )
        print(f"Created admin membership on data company (default=True)")

    others = await db.companymembership.find_many(where={"userId": user_id})
    for m in others:
        if m.companyId == data_company_id:
            continue
        if m.isDefault:
            await db.companymembership.update(
                where={"id": m.id}, data={"isDefault": False}
            )
            print(f"  Cleared default on company {m.companyId}")


async def mode_move(
    db: Prisma, user_id: str, source_id: str, target_id: str
) -> None:
    if source_id == target_id:
        print("Source and target company are the same — nothing to move.")
        return

    src_company = await db.company.find_unique(where={"id": source_id})
    tgt_company = await db.company.find_unique(where={"id": target_id})
    if not src_company or not tgt_company:
        raise SystemExit("Source or target company not found")

    print(f"Moving data: {src_company.name} ({source_id})")
    print(f"         -> {tgt_company.name} ({target_id})")

    tables = await tables_with_company_id(db)

    # Remove target stubs that would block singleton merge.
    for table in SINGLETON_TABLES:
        if table not in tables:
            continue
        n = await count_for(db, table, target_id)
        if n:
            await db.execute_raw(
                f'DELETE FROM "{table}" WHERE company_id = $1', target_id
            )
            print(f"  Deleted {n} stub row(s) from {table} @ target")

    # Delete other target seed rows when source has real data (avoid duplicate codes after merge).
    seed_tables = (
        "bank_accounts",
        "bank_payments",
        "journals",
        "document_number_sequences",
    )
    for table in seed_tables:
        if table not in tables:
            continue
        src_n = await count_for(db, table, source_id)
        tgt_n = await count_for(db, table, target_id)
        if src_n and tgt_n:
            await db.execute_raw(
                f'DELETE FROM "{table}" WHERE company_id = $1', target_id
            )
            print(f"  Deleted {tgt_n} seed row(s) from {table} @ target")

    moved_total = 0
    for table in tables:
        src_n = await count_for(db, table, source_id)
        if not src_n:
            continue
        await db.execute_raw(
            f'UPDATE "{table}" SET company_id = $1 WHERE company_id = $2',
            target_id,
            source_id,
        )
        moved_total += src_n
        print(f"  {table}: moved {src_n} rows")

    print(f"\nMoved {moved_total} rows total to {tgt_company.name}")

    # Ensure user stays default on target (already should be).
    mem = await db.companymembership.find_unique(
        where={"companyId_userId": {"companyId": target_id, "userId": user_id}}
    )
    if mem and not mem.isDefault:
        await db.companymembership.update(
            where={"id": mem.id}, data={"isDefault": True}
        )


async def verify(db: Prisma, user_id: str, company_id: str) -> None:
    user = await db.user.find_unique(where={"id": user_id})
    print(f"\n=== Verification for {user.email if user else user_id} ===")
    mems = await db.companymembership.find_many(
        where={"userId": user_id}, include={"company": True}
    )
    for m in mems:
        c = m.company
        inv = await db.salesinvoice.count(where={"companyId": c.id})
        cust = await db.customer.count(where={"companyId": c.id})
        print(
            f"  {c.name!r} default={m.isDefault} customers={cust} invoices={inv}"
        )
    active = next((m for m in mems if m.isDefault), mems[0])
    if active.companyId != company_id:
        print(f"  (default company is {active.companyId}, not {company_id})")


async def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--user-id", required=True)
    p.add_argument(
        "--mode",
        choices=("link", "move", "both"),
        default="both",
        help="link=membership on data company; move=data to user's company; both=move+ensure membership",
    )
    p.add_argument("--data-company-id", default=DATA_COMPANY_ID)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    db = Prisma()
    await db.connect()
    try:
        target_id, target_name = await user_default_company(db, args.user_id)
        print(f"User default company: {target_name} ({target_id})")
        data_id = args.data_company_id
        src_inv = await db.salesinvoice.count(where={"companyId": data_id})
        print(f"Data company invoices: {src_inv}")

        if args.dry_run:
            print("DRY RUN — no changes applied")
            await verify(db, args.user_id, target_id)
            return

        if args.mode in ("move", "both"):
            await mode_move(db, args.user_id, data_id, target_id)
        if args.mode in ("link", "both"):
            # After move, data lives on target — link is satisfied by existing membership.
            if args.mode == "link":
                await mode_link(db, args.user_id, data_id)
            else:
                role_id = await admin_role_id(db, target_id)
                mem = await db.companymembership.find_unique(
                    where={
                        "companyId_userId": {
                            "companyId": target_id,
                            "userId": args.user_id,
                        }
                    }
                )
                if mem and mem.roleId != role_id:
                    await db.companymembership.update(
                        where={"id": mem.id}, data={"roleId": role_id, "isDefault": True}
                    )

        await verify(db, args.user_id, target_id)
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
