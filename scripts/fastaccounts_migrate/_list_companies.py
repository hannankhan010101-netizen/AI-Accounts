import asyncio
import json
import os
import sys
from pathlib import Path

# Backend prisma
ROOT = Path(__file__).resolve().parents[2] / "Backend"
sys.path.insert(0, str(ROOT / "src"))
os.chdir(ROOT)

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from prisma_generated import Prisma


async def main():
    db = Prisma()
    await db.connect()
    companies = await db.company.find_many()
    for c in companies:
        n = await db.customer.count(where={"companyId": c.id})
        print(c.id, c.name, "customers:", n)
    await db.disconnect()


asyncio.run(main())
