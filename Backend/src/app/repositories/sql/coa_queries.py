"""Flat SQL for chart-of-accounts tree (Phase 5 — single round trip)."""

from __future__ import annotations

from typing import Any

COA_FLAT_TREE_SQL = """
SELECT
  c.id AS "categoryId",
  c.code AS "categoryCode",
  c.name AS "categoryName",
  c.sort_order AS "categorySortOrder",
  c.category_type AS "categoryType",
  s.id AS "sectionId",
  s.code AS "sectionCode",
  s.name AS "sectionName",
  s.sort_order AS "sectionSortOrder",
  n.id AS "nominalId",
  n.code AS "nominalCode",
  n.name AS "nominalName",
  n.description AS "nominalDescription",
  n.is_charge_deduction AS "isChargeDeduction"
FROM coa_categories c
LEFT JOIN coa_sections s ON s.category_id = c.id
LEFT JOIN nominal_accounts n ON n.section_id = s.id
WHERE c.company_id = $1
ORDER BY c.sort_order ASC, s.sort_order ASC NULLS LAST, n.code ASC NULLS LAST
"""


def build_coa_tree_from_flat(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Assemble category → section → nominal hierarchy from a flat join result."""

    categories: dict[str, dict[str, Any]] = {}
    section_index: dict[tuple[str, str], dict[str, Any]] = {}

    for row in rows:
        cat_id = row.get("categoryId")
        if cat_id is None:
            continue
        cat_key = str(cat_id)
        if cat_key not in categories:
            categories[cat_key] = {
                "id": cat_id,
                "code": row.get("categoryCode"),
                "name": row.get("categoryName"),
                "sortOrder": row.get("categorySortOrder"),
                "categoryType": row.get("categoryType"),
                "sections": [],
            }

        sec_id = row.get("sectionId")
        if sec_id is None:
            continue
        sec_key = (cat_key, str(sec_id))
        if sec_key not in section_index:
            section = {
                "id": sec_id,
                "code": row.get("sectionCode"),
                "name": row.get("sectionName"),
                "sortOrder": row.get("sectionSortOrder"),
                "nominals": [],
            }
            section_index[sec_key] = section
            categories[cat_key]["sections"].append(section)

        nom_id = row.get("nominalId")
        if nom_id is None:
            continue
        section_index[sec_key]["nominals"].append(
            {
                "id": nom_id,
                "code": row.get("nominalCode"),
                "name": row.get("nominalName"),
                "description": row.get("nominalDescription"),
                "isChargeDeduction": row.get("isChargeDeduction"),
            }
        )

    return sorted(categories.values(), key=lambda c: c.get("sortOrder") or 0)
