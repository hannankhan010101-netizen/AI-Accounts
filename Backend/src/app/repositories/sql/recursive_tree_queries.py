"""Reusable ``WITH RECURSIVE`` templates for future nested hierarchies.

Not wired to live schema today — COA uses fixed-depth flat JOINs in ``coa_queries.py``.
When adding ``parent_id`` trees (product categories, org chart), use this pattern and
index ``(company_id, parent_id)``.
"""

from __future__ import annotations

# Placeholder table/column names — replace when a hierarchy model is added.
RECURSIVE_TREE_TEMPLATE = """
WITH RECURSIVE tree AS (
  SELECT
    n.id,
    n.parent_id AS "parentId",
    n.name,
    1 AS depth,
    ARRAY[n.id] AS path
  FROM hierarchy_nodes n
  WHERE n.company_id = $1
    AND n.parent_id IS NULL
  UNION ALL
  SELECT
    c.id,
    c.parent_id,
    c.name,
    t.depth + 1,
    t.path || c.id
  FROM hierarchy_nodes c
  INNER JOIN tree t ON c.parent_id = t.id
  WHERE c.company_id = $1
    AND NOT c.id = ANY(t.path)
)
SELECT id, "parentId", name, depth, path
FROM tree
ORDER BY path
"""

# Self-contained validation query (creates temp table in tests only).
RECURSIVE_TREE_SELF_TEST_DDL = """
CREATE TEMP TABLE IF NOT EXISTS _tree_test (
  id text PRIMARY KEY,
  company_id text NOT NULL,
  parent_id text,
  name text NOT NULL
) ON COMMIT DROP
"""

RECURSIVE_TREE_SELF_TEST_SEED = """
INSERT INTO _tree_test (id, company_id, parent_id, name) VALUES
  ('root', 'co1', NULL, 'Root'),
  ('a', 'co1', 'root', 'A'),
  ('b', 'co1', 'root', 'B'),
  ('a1', 'co1', 'a', 'A1')
ON CONFLICT DO NOTHING
"""

RECURSIVE_TREE_SELF_TEST_QUERY = """
WITH RECURSIVE tree AS (
  SELECT id, parent_id, name, 1 AS depth, ARRAY[id] AS path
  FROM _tree_test
  WHERE company_id = $1 AND parent_id IS NULL
  UNION ALL
  SELECT c.id, c.parent_id, c.name, t.depth + 1, t.path || c.id
  FROM _tree_test c
  INNER JOIN tree t ON c.parent_id = t.id
  WHERE c.company_id = $1 AND NOT c.id = ANY(t.path)
)
SELECT id, name, depth FROM tree ORDER BY path
"""
