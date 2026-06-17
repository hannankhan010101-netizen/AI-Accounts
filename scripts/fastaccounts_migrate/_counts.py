import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "Backend"
sys.path.insert(0, str(ROOT / "src"))

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")

from prisma_generated import Prisma

CID = "cmpfl1itj000hqubj7rne8q5f"


async def main():
    db = Prisma()
    await db.connect()
    counts = {
        "customers": await db.customer.count(where={"companyId": CID}),
        "suppliers": await db.supplier.count(where={"companyId": CID}),
        "products": await db.product.count(where={"companyId": CID}),
        "bank_accounts": await db.bankaccount.count(where={"companyId": CID}),
        "nominals": await db.nominalaccount.count(
            where={"section": {"is": {"category": {"is": {"companyId": CID}}}}}
        ),
        "invoices": await db.salesinvoice.count(where={"companyId": CID}),
        "bills": await db.supplierbill.count(where={"companyId": CID}),
        "receipts": await db.salesreceipt.count(where={"companyId": CID}),
        "bank_payments": await db.bankpayment.count(where={"companyId": CID}),
        "journals": await db.journal.count(where={"companyId": CID}),
    }
    for k, v in counts.items():
        print(f"{k}: {v}")
    await db.disconnect()


asyncio.run(main())
