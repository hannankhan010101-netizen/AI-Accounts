"""Taxes and year-end configuration aggregate."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from prisma_generated import Prisma
from prisma_generated.models import TaxesYearEndConfig


class TaxesConfigRepository:
    """Read/update tax grids and year-end date."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def get_for_company(self, *, company_id: str) -> TaxesYearEndConfig | None:
        """Return tax configuration row."""

        return await self._db.taxesyearendconfig.find_unique(where={"companyId": company_id})

    async def upsert_full(
        self,
        *,
        company_id: str,
        year_end_date: datetime | None,
        tax_display: dict[str, Any],
        gst_rates: list[Any],
        fed_rates: list[Any],
        adt_rates: list[Any],
        wht_rates: list[Any],
        tax_regions: list[Any],
    ) -> TaxesYearEndConfig:
        """Replace tax document for tenant."""

        return await self._db.taxesyearendconfig.upsert(
            where={"companyId": company_id},
            data={
                "create": {
                    "companyId": company_id,
                    "yearEndDate": year_end_date,
                    "taxDisplay": tax_display,
                    "gstRates": gst_rates,
                    "fedRates": fed_rates,
                    "adtRates": adt_rates,
                    "whtRates": wht_rates,
                    "taxRegions": tax_regions,
                },
                "update": {
                    "yearEndDate": year_end_date,
                    "taxDisplay": tax_display,
                    "gstRates": gst_rates,
                    "fedRates": fed_rates,
                    "adtRates": adt_rates,
                    "whtRates": wht_rates,
                    "taxRegions": tax_regions,
                },
            },
        )
