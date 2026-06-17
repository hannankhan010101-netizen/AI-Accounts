import asyncio
import sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[2] / "Backend"
sys.path.insert(0, str(ROOT / "src"))
from dotenv import load_dotenv
load_dotenv(ROOT / ".env")
from prisma_generated import Prisma

CID = "cmpfl1itj000hqubj7rne8q5f"

async def main():
    db = Prisma()
    await db.connect()
    invs = await db.salesinvoice.find_many(where={"companyId": CID})
    bills = await db.supplierbill.find_many(where={"companyId": CID})
    inv_nums = Counter(i.invoiceNumber for i in invs)
    bill_nums = Counter(b.billNumber for b in bills)
    inv_dupes = sum(1 for n, c in inv_nums.items() if c > 1)
    bill_dupes = sum(1 for n, c in bill_nums.items() if c > 1)
    print(f"invoices total={len(invs)} unique_numbers={len(inv_nums)} duplicate_numbers={inv_dupes}")
    print(f"bills total={len(bills)} unique_numbers={len(bill_nums)} duplicate_numbers={bill_dupes}")
    await db.disconnect()

asyncio.run(main())
