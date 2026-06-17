#!/usr/bin/env python3
"""List tables with company_id and row counts per company."""
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

SOURCE = "cmpfl1itj000hqubj7rne8q5f"
TARGET = "cmpfm1nst0001lhq3rz09938z"


async def main() -> None:
    db = Prisma()
    await db.connect()
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
    print(f"Tables with company_id: {len(rows)}")
    total_src = 0
    total_tgt = 0
    for r in rows:
        t = r["table_name"]
        try:
            cnt = await db.query_raw(
                f'SELECT COUNT(*)::int AS n FROM "{t}" WHERE company_id = $1',
                SOURCE,
            )
            n = cnt[0]["n"]
            if n:
                total_src += n
                print(f"  {t}: {n} rows @ source")
            cnt2 = await db.query_raw(
                f'SELECT COUNT(*)::int AS n FROM "{t}" WHERE company_id = $1',
                TARGET,
            )
            n2 = cnt2[0]["n"]
            if n2:
                total_tgt += n2
                print(f"  {t}: {n2} rows @ target (HAK)")
        except Exception as e:
            print(f"  {t}: ERROR {e}")
    print(f"\nTotal rows at source: {total_src}, at target: {total_tgt}")
    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
