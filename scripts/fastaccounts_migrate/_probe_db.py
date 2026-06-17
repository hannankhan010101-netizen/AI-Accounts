#!/usr/bin/env python3
import asyncio
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "Backend"
sys.path.insert(0, str(ROOT / "src"))
from dotenv import load_dotenv

load_dotenv(ROOT / ".env")

from prisma_generated import Prisma


async def probe(label: str, url: str) -> None:
    os.environ["DATABASE_URL"] = url
    db = Prisma()
    await db.connect()
    rows = await db.query_raw(
        """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY 1
        """
    )
    print(f"{label}: {len(rows)} tables, sample={[r['table_name'] for r in rows[:15]]}")
    await db.disconnect()


async def main() -> None:
    pooler = os.environ.get("DATABASE_URL", "")
    direct = os.environ.get("DIRECT_URL", "")
    if pooler:
        await probe("pooler", pooler)
    if direct:
        await probe("direct", direct)


if __name__ == "__main__":
    asyncio.run(main())
