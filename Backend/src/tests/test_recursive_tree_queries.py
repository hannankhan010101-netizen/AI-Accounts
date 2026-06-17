"""Recursive CTE template validation (Step 1 future hierarchies)."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")

from app.repositories.sql import recursive_tree_queries as rtq


def test_recursive_tree_template_has_anchor_and_recursive_parts() -> None:
    sql = rtq.RECURSIVE_TREE_TEMPLATE.lower()
    assert "with recursive tree as" in sql
    assert "union all" in sql
    assert "parent_id" in sql


def test_recursive_tree_self_test_query_structure() -> None:
    sql = rtq.RECURSIVE_TREE_SELF_TEST_QUERY.lower()
    assert "with recursive tree as" in sql
    assert "_tree_test" in sql
    assert "order by path" in sql
