"""Shared SQL CTE patterns for query consolidation (Step 1 performance).

Use flat JOINs for fixed-depth hierarchies (e.g. COA category → section → nominal).
Use ``WITH RECURSIVE`` only for variable-depth parent-child graphs — see
``recursive_tree_queries.py``.
"""

from __future__ import annotations

# Documented parameter order for company-scoped date-range filters:
# $1 company_id, $2 date_from (nullable timestamptz), $3 date_to (nullable timestamptz)

DATE_RANGE_JOURNAL_FILTER = """
  AND ($2::timestamptz IS NULL OR j.journal_date >= $2::timestamptz)
  AND ($3::timestamptz IS NULL OR j.journal_date <= $3::timestamptz)
"""
