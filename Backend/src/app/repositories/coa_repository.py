"""Chart of accounts read/write models — catalog §9.1."""

from __future__ import annotations

import hashlib
from typing import Any

from prisma_generated import Prisma
from prisma_generated.models import CoaCategory, CoaSection, NominalAccount

from app.core.async_io import maybe_thread
from app.repositories.sql.coa_queries import COA_FLAT_TREE_SQL, build_coa_tree_from_flat


class CoaRepository:
    """Category / section / nominal queries and mutations."""

    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    @staticmethod
    def tree_etag(revision_token: str) -> str:
        return hashlib.sha256(revision_token.encode()).hexdigest()[:32]

    async def tree_revision_token(self, *, company_id: str) -> str:
        """Stable revision string for COA tree HTTP caching."""

        rows = await self._db.query_raw(
            """
            SELECT md5(
              concat_ws('|',
                (SELECT count(*)::text FROM coa_categories WHERE company_id = $1),
                (SELECT count(*)::text FROM coa_sections s
                   JOIN coa_categories c ON c.id = s.category_id
                  WHERE c.company_id = $1),
                (SELECT count(*)::text FROM nominal_accounts n
                   JOIN coa_sections s ON s.id = n.section_id
                   JOIN coa_categories c ON c.id = s.category_id
                  WHERE c.company_id = $1)
              )
            ) AS rev
            """,
            company_id,
        )
        if not rows:
            return "0"
        row = rows[0]
        return str(row.get("rev") or row.get("Rev") or "0")

    async def list_categories(self, *, company_id: str) -> list[CoaCategory]:
        """Top-level COA categories for the chart browser."""

        return await self._db.coacategory.find_many(
            where={"companyId": company_id},
            order={"sortOrder": "asc"},
            take=200,
        )

    async def list_tree(self, *, company_id: str) -> list[dict[str, Any]]:
        """Return categories → sections → nominals as a nested list for §9.1.1."""

        rows = await self._db.query_raw(COA_FLAT_TREE_SQL, company_id)
        flat = [dict(r) for r in rows]
        return await maybe_thread(
            build_coa_tree_from_flat,
            flat,
            min_rows=500,
            row_count=len(flat),
        )

    async def list_sections(self, *, company_id: str) -> list[dict[str, Any]]:
        """Sections joined with their category for the Section listing screen."""

        rows = await self._db.coasection.find_many(
            where={"category": {"is": {"companyId": company_id}}},
            order={"sortOrder": "asc"},
            include={"category": True},
            take=500,
        )
        return [
            {
                "id": s.id,
                "code": s.code,
                "name": s.name,
                "sortOrder": s.sortOrder,
                "categoryId": s.categoryId,
                "categoryName": s.category.name if s.category else None,  # type: ignore[union-attr]
                "categoryCode": s.category.code if s.category else None,  # type: ignore[union-attr]
            }
            for s in rows
        ]

    async def create_category(
        self,
        *,
        company_id: str,
        code: str,
        name: str,
        category_type: str = "Other",
        sort_order: int = 0,
    ) -> CoaCategory:
        """Create a top-level COA category (previously impossible via the app)."""

        allowed = {"Income", "Expense", "Asset", "Liability", "Equity", "Other"}
        if category_type not in allowed:
            raise ValueError(f"categoryType must be one of {sorted(allowed)}")
        return await self._db.coacategory.create(
            data={
                "companyId": company_id,
                "code": code,
                "name": name,
                "categoryType": category_type,
                "sortOrder": sort_order,
            },
        )

    async def seed_default_chart(self, *, company_id: str) -> bool:
        """Seed the standard starter chart if the company has none.

        Idempotent: returns ``False`` (and does nothing) when any category
        already exists, so it is safe to call on every login/bootstrap.
        """

        from app.constants.default_chart_of_accounts import DEFAULT_CHART

        existing = await self._db.coacategory.count(where={"companyId": company_id})
        if existing:
            return False

        for c_order, cat in enumerate(DEFAULT_CHART):
            category = await self.create_category(
                company_id=company_id,
                code=str(cat["code"]),
                name=str(cat["name"]),
                category_type=str(cat["type"]),
                sort_order=c_order,
            )
            for s_order, sec in enumerate(cat["sections"]):
                section = await self._db.coasection.create(
                    data={
                        "categoryId": category.id,
                        "code": str(sec["code"]),
                        "name": str(sec["name"]),
                        "sortOrder": s_order,
                    },
                )
                for nom in sec["nominals"]:
                    await self._db.nominalaccount.create(
                        data={
                            "sectionId": section.id,
                            "code": str(nom["code"]),
                            "name": str(nom["name"]),
                        },
                    )
        return True

    async def create_section(
        self,
        *,
        company_id: str,
        category_id: str,
        code: str,
        name: str,
    ) -> CoaSection:
        """Create a section under a category, validating tenancy."""

        category = await self._db.coacategory.find_unique(where={"id": category_id})
        if category is None or category.companyId != company_id:
            raise ValueError("Category not found for this company")

        existing = await self._db.coasection.find_many(
            where={"categoryId": category_id},
            order={"sortOrder": "desc"},
            take=1,
        )
        next_order = (existing[0].sortOrder + 1) if existing else 0

        return await self._db.coasection.create(
            data={
                "categoryId": category_id,
                "code": code,
                "name": name,
                "sortOrder": next_order,
            },
        )

    async def reorder_section(
        self,
        *,
        company_id: str,
        section_id: str,
        direction: str,
    ) -> CoaSection:
        """Swap sortOrder with the neighbour above/below within the same category."""

        section = await self._db.coasection.find_unique(
            where={"id": section_id},
            include={"category": True},
        )
        if section is None or section.category.companyId != company_id:  # type: ignore[union-attr]
            raise ValueError("Section not found for this company")

        op = "lt" if direction == "up" else "gt"
        order_dir = "desc" if direction == "up" else "asc"
        neighbours = await self._db.coasection.find_many(
            where={
                "categoryId": section.categoryId,
                "sortOrder": {op: section.sortOrder},
            },
            order={"sortOrder": order_dir},
            take=1,
        )
        if not neighbours:
            return section
        neighbour = neighbours[0]

        await self._db.coasection.update(
            where={"id": neighbour.id},
            data={"sortOrder": section.sortOrder},
        )
        return await self._db.coasection.update(
            where={"id": section.id},
            data={"sortOrder": neighbour.sortOrder},
        )

    async def update_category_type(
        self,
        *,
        company_id: str,
        category_id: str,
        category_type: str,
    ) -> CoaCategory:
        """Set the P&L/BS classification on a category (§9.1.1)."""

        allowed = {"Income", "Expense", "Asset", "Liability", "Equity", "Other"}
        if category_type not in allowed:
            raise ValueError(f"categoryType must be one of {sorted(allowed)}")

        category = await self._db.coacategory.find_unique(where={"id": category_id})
        if category is None or category.companyId != company_id:
            raise ValueError("Category not found for this company")

        return await self._db.coacategory.update(
            where={"id": category_id},
            data={"categoryType": category_type},
        )

    async def create_nominal(
        self,
        *,
        company_id: str,
        section_id: str,
        code: str,
        name: str,
        description: str | None,
        is_charge_deduction: bool,
    ) -> NominalAccount:
        """Create a nominal under a section, validating tenancy."""

        section = await self._db.coasection.find_unique(
            where={"id": section_id},
            include={"category": True},
        )
        if section is None or section.category.companyId != company_id:  # type: ignore[union-attr]
            raise ValueError("Section not found for this company")

        return await self._db.nominalaccount.create(
            data={
                "sectionId": section_id,
                "code": code,
                "name": name,
                "description": description,
                "isChargeDeduction": is_charge_deduction,
            },
        )

    async def get_nominal(
        self, *, company_id: str, nominal_id: str
    ) -> NominalAccount | None:
        row = await self._db.nominalaccount.find_unique(
            where={"id": nominal_id},
            include={"section": {"include": {"category": True}}},
        )
        if row is None or row.section.category.companyId != company_id:  # type: ignore[union-attr]
            return None
        return row

    async def update_nominal(
        self,
        *,
        company_id: str,
        nominal_id: str,
        name: str | None = None,
        description: str | None = None,
        is_charge_deduction: bool | None = None,
    ) -> NominalAccount:
        row = await self.get_nominal(company_id=company_id, nominal_id=nominal_id)
        if row is None:
            raise ValueError("Nominal not found for this company")

        data: dict = {}
        if name is not None:
            data["name"] = name
        if description is not None:
            data["description"] = description
        if is_charge_deduction is not None:
            data["isChargeDeduction"] = is_charge_deduction
        if not data:
            return row
        return await self._db.nominalaccount.update(
            where={"id": nominal_id},
            data=data,
        )

    async def move_nominal(
        self,
        *,
        company_id: str,
        nominal_id: str,
        section_id: str,
    ) -> NominalAccount:
        row = await self.get_nominal(company_id=company_id, nominal_id=nominal_id)
        if row is None:
            raise ValueError("Nominal not found for this company")

        section = await self._db.coasection.find_unique(
            where={"id": section_id},
            include={"category": True},
        )
        if section is None or section.category.companyId != company_id:  # type: ignore[union-attr]
            raise ValueError("Target section not found for this company")

        return await self._db.nominalaccount.update(
            where={"id": nominal_id},
            data={"sectionId": section_id},
        )

    async def nominal_ids_by_codes(
        self, *, company_id: str, codes: list[str]
    ) -> dict[str, str]:
        """Map nominal code → ``NominalAccount.id`` for this company."""

        if not codes:
            return {}
        found = await self._db.nominalaccount.find_many(
            where={
                "code": {"in": codes},
                "section": {"is": {"category": {"is": {"companyId": company_id}}}},
            },
        )
        return {n.code: n.id for n in found}

    async def missing_nominal_codes(
        self, *, company_id: str, codes: list[str]
    ) -> list[str]:
        """Return codes from ``codes`` that are not on this company's chart."""

        if not codes:
            return []
        found = await self._db.nominalaccount.find_many(
            where={
                "code": {"in": codes},
                "section": {"is": {"category": {"is": {"companyId": company_id}}}},
            },
        )
        found_set = {n.code for n in found}
        return sorted(c for c in codes if c not in found_set)

    async def _journal_line_usage_count(
        self, *, company_id: str, nominal_id: str, nominal_code: str
    ) -> int:
        return await self._db.journalline.count(
            where={
                "OR": [
                    {"nominalAccountId": nominal_id},
                    {
                        "nominalCode": nominal_code,
                        "journal": {"is": {"companyId": company_id}},
                    },
                ]
            }
        )

    async def delete_nominal(self, *, company_id: str, nominal_id: str) -> None:
        row = await self.get_nominal(company_id=company_id, nominal_id=nominal_id)
        if row is None:
            raise ValueError("Nominal not found for this company")
        usage = await self._journal_line_usage_count(
            company_id=company_id,
            nominal_id=nominal_id,
            nominal_code=row.code,
        )
        if usage > 0:
            raise ValueError(
                f"Nominal {row.code} has {usage} journal line(s) and cannot be deleted"
            )
        await self._db.nominalaccount.delete(where={"id": nominal_id})

    async def bulk_delete_nominals(
        self, *, company_id: str, nominal_ids: list[str]
    ) -> dict[str, int]:
        deleted = 0
        skipped = 0
        for nominal_id in nominal_ids:
            try:
                await self.delete_nominal(company_id=company_id, nominal_id=nominal_id)
                deleted += 1
            except ValueError:
                skipped += 1
        return {"deleted": deleted, "skipped": skipped}
