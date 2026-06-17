"""Seed missing RBAC role templates for all existing companies."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from prisma_generated import Prisma  # noqa: E402
from app.repositories.company_bootstrap_repository import CompanyBootstrapRepository  # noqa: E402


async def main() -> None:
    db = Prisma()
    await db.connect()
    bootstrap = CompanyBootstrapRepository(db)
    companies = await db.company.find_many(order={"createdAt": "asc"})
    total_created = 0
    for company in companies:
        created = await bootstrap.seed_missing_template_roles(company_id=company.id)
        if created:
            print(f"{company.name} ({company.id}): +{len(created)} roles")
            for row in created:
                print(f"  - {row['name']} ({row['code']})")
            total_created += len(created)
    print(f"Done. Created {total_created} role(s) across {len(companies)} companies.")
    await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
