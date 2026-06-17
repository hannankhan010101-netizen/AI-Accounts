"""Parameterized SQL for journal / GL aggregates (Phase 1 performance)."""

from __future__ import annotations

TRIAL_BALANCE_SQL = """
SELECT
  jl.nominal_code AS "nominalCode",
  COALESCE(MAX(na.name), jl.nominal_code) AS name,
  SUM(jl.debit) AS debit,
  SUM(jl.credit) AS credit,
  SUM(jl.debit - jl.credit) AS balance
FROM journal_lines jl
INNER JOIN journals j ON j.id = jl.journal_id
LEFT JOIN nominal_accounts na ON na.code = jl.nominal_code
LEFT JOIN coa_sections s ON s.id = na.section_id
LEFT JOIN coa_categories c ON c.id = s.category_id AND c.company_id = j.company_id
WHERE j.company_id = $1
  AND j.status = 'posted'
  AND ($2::timestamptz IS NULL OR j.journal_date <= $2::timestamptz)
GROUP BY jl.nominal_code
ORDER BY jl.nominal_code
"""

GL_OPENING_BALANCE_SQL = """
SELECT COALESCE(SUM(jl.debit - jl.credit), 0) AS opening
FROM journal_lines jl
INNER JOIN journals j ON j.id = jl.journal_id
WHERE j.company_id = $1
  AND j.status = 'posted'
  AND jl.nominal_code = $2
  AND ($3::timestamptz IS NULL OR j.journal_date < $3)
"""

GL_ACTIVITY_SQL = """
SELECT
  jl.id AS line_id,
  jl.journal_id AS "journalId",
  j.journal_number AS "journalNumber",
  j.journal_date AS "journalDate",
  j.ref_no AS "refNo",
  jl.project_code AS "projectCode",
  jl.debit,
  jl.credit
FROM journal_lines jl
INNER JOIN journals j ON j.id = jl.journal_id
WHERE j.company_id = $1
  AND j.status = 'posted'
  AND jl.nominal_code = $2
  AND ($3::timestamptz IS NULL OR j.journal_date >= $3::timestamptz)
  AND ($4::timestamptz IS NULL OR j.journal_date <= $4::timestamptz)
ORDER BY j.journal_date ASC, j.id ASC, jl.id ASC
LIMIT $5
"""

GL_ACTIVITY_COUNT_SQL = """
SELECT COUNT(*)::bigint AS cnt
FROM journal_lines jl
INNER JOIN journals j ON j.id = jl.journal_id
WHERE j.company_id = $1
  AND j.status = 'posted'
  AND jl.nominal_code = $2
  AND ($3::timestamptz IS NULL OR j.journal_date >= $3::timestamptz)
  AND ($4::timestamptz IS NULL OR j.journal_date <= $4::timestamptz)
"""

CLASSIFIED_BALANCES_SQL = """
SELECT
  jl.nominal_code AS "nominalCode",
  MAX(na.name) AS name,
  COALESCE(MAX(c.category_type), 'Other') AS "categoryType",
  COALESCE(MAX(c.name), 'Uncategorized') AS "categoryName",
  SUM(jl.debit) AS debit,
  SUM(jl.credit) AS credit,
  SUM(jl.debit - jl.credit) AS balance
FROM journal_lines jl
INNER JOIN journals j ON j.id = jl.journal_id
LEFT JOIN nominal_accounts na ON na.code = jl.nominal_code
LEFT JOIN coa_sections s ON s.id = na.section_id
LEFT JOIN coa_categories c ON c.id = s.category_id AND c.company_id = j.company_id
WHERE j.company_id = $1
  AND j.status = 'posted'
  AND ($2::timestamptz IS NULL OR j.journal_date >= $2::timestamptz)
  AND ($3::timestamptz IS NULL OR j.journal_date <= $3::timestamptz)
GROUP BY jl.nominal_code
ORDER BY jl.nominal_code
"""

MONTHLY_TB_TOTALS_SQL = """
WITH months AS (
  SELECT
    (
      date_trunc('month', $2::timestamptz AT TIME ZONE 'UTC')
      - (gs.n || ' months')::interval
      + interval '1 month'
      - interval '1 day'
    )::timestamptz AS period_end,
    to_char(
      date_trunc('month', $2::timestamptz AT TIME ZONE 'UTC') - (gs.n || ' months')::interval,
      'YYYY-MM'
    ) AS period_key
  FROM generate_series(0, $3::int - 1) AS gs(n)
)
SELECT
  m.period_key AS period,
  m.period_end::date AS "periodTo",
  COUNT(DISTINCT jl.nominal_code)::int AS "accountCount",
  COALESCE(SUM(jl.debit), 0) AS "totalDebit",
  COALESCE(SUM(jl.credit), 0) AS "totalCredit"
FROM months m
LEFT JOIN journals j
  ON j.company_id = $1
  AND j.status = 'posted'
  AND j.journal_date <= m.period_end
LEFT JOIN journal_lines jl ON jl.journal_id = j.id
GROUP BY m.period_key, m.period_end
ORDER BY m.period_key ASC
"""

MONTHLY_CLASSIFIED_PNL_SQL = """
WITH months AS (
  SELECT
    date_trunc(
      'month',
      $2::timestamptz AT TIME ZONE 'UTC' - (gs.n || ' months')::interval
    ) AS period_start,
    (
      date_trunc(
        'month',
        $2::timestamptz AT TIME ZONE 'UTC' - (gs.n || ' months')::interval
      )
      + interval '1 month'
      - interval '1 second'
    )::timestamptz AS period_end,
    to_char(
      date_trunc(
        'month',
        $2::timestamptz AT TIME ZONE 'UTC' - (gs.n || ' months')::interval
      ),
      'YYYY-MM'
    ) AS period_key
  FROM generate_series(0, $3::int - 1) AS gs(n)
)
SELECT
  m.period_key AS period,
  m.period_start AS "periodFrom",
  m.period_end AS "periodTo",
  COALESCE(
    SUM(jl.debit - jl.credit) FILTER (WHERE c.category_type = 'Income'),
    0
  ) AS "totalIncome",
  COALESCE(
    SUM(jl.debit - jl.credit) FILTER (WHERE c.category_type = 'Expense'),
    0
  ) AS "totalExpense"
FROM months m
LEFT JOIN journals j
  ON j.company_id = $1
  AND j.status = 'posted'
  AND j.journal_date >= m.period_start
  AND j.journal_date <= m.period_end
LEFT JOIN journal_lines jl ON jl.journal_id = j.id
LEFT JOIN nominal_accounts na ON na.code = jl.nominal_code
LEFT JOIN coa_sections s ON s.id = na.section_id
LEFT JOIN coa_categories c ON c.id = s.category_id AND c.company_id = j.company_id
GROUP BY m.period_key, m.period_start, m.period_end
ORDER BY m.period_key ASC
"""

MONTHLY_CLASSIFIED_PNL_BY_CATEGORY_SQL = """
WITH months AS (
  SELECT
    date_trunc(
      'month',
      $2::timestamptz AT TIME ZONE 'UTC' - (gs.n || ' months')::interval
    ) AS period_start,
    (
      date_trunc(
        'month',
        $2::timestamptz AT TIME ZONE 'UTC' - (gs.n || ' months')::interval
      )
      + interval '1 month'
      - interval '1 second'
    )::timestamptz AS period_end,
    to_char(
      date_trunc(
        'month',
        $2::timestamptz AT TIME ZONE 'UTC' - (gs.n || ' months')::interval
      ),
      'YYYY-MM'
    ) AS period_key
  FROM generate_series(0, $3::int - 1) AS gs(n)
),
per_nominal AS (
  SELECT
    m.period_key,
    COALESCE(c.category_type, 'Other') AS category_type,
    COALESCE(c.name, 'Uncategorized') AS category_name,
    SUM(jl.debit - jl.credit) AS balance
  FROM months m
  INNER JOIN journals j
    ON j.company_id = $1
    AND j.status = 'posted'
    AND j.journal_date >= m.period_start
    AND j.journal_date <= m.period_end
  INNER JOIN journal_lines jl ON jl.journal_id = j.id
  LEFT JOIN nominal_accounts na ON na.code = jl.nominal_code
  LEFT JOIN coa_sections s ON s.id = na.section_id
  LEFT JOIN coa_categories c ON c.id = s.category_id AND c.company_id = j.company_id
  GROUP BY m.period_key, jl.nominal_code, c.category_type, c.name
)
SELECT
  period_key AS period,
  category_type AS "categoryType",
  category_name AS "categoryName",
  SUM(balance) AS amount
FROM per_nominal
WHERE category_type IN ('Income', 'Expense')
GROUP BY period_key, category_type, category_name
ORDER BY period_key ASC, category_type ASC, category_name ASC
"""

# Max GL activity lines returned in one request (raise if exceeded).
GL_ACTIVITY_MAX_LINES = 50_000

GL_FULL_SQL = """
WITH opening AS (
  SELECT COALESCE(SUM(jl.debit - jl.credit), 0) AS bal
  FROM journal_lines jl
  INNER JOIN journals j ON j.id = jl.journal_id
  WHERE j.company_id = $1
    AND j.status = 'posted'
    AND jl.nominal_code = $2
    AND ($3::timestamptz IS NULL OR j.journal_date < $3)
),
filtered AS (
  SELECT
    jl.id AS line_id,
    jl.journal_id AS "journalId",
    j.journal_number AS "journalNumber",
    j.journal_date AS "journalDate",
    j.ref_no AS "refNo",
    jl.project_code AS "projectCode",
    jl.debit,
    jl.credit
  FROM journal_lines jl
  INNER JOIN journals j ON j.id = jl.journal_id
  WHERE j.company_id = $1
    AND j.status = 'posted'
    AND jl.nominal_code = $2
    AND ($3::timestamptz IS NULL OR j.journal_date >= $3::timestamptz)
    AND ($4::timestamptz IS NULL OR j.journal_date <= $4::timestamptz)
),
activity_count AS (
  SELECT COUNT(*)::bigint AS cnt FROM filtered
),
activity AS (
  SELECT
    f.line_id,
    f."journalId",
    f."journalNumber",
    f."journalDate",
    f."refNo",
    f."projectCode",
    f.debit,
    f.credit,
    o.bal + SUM(f.debit - f.credit) OVER (
      ORDER BY f."journalDate" ASC, f."journalId" ASC, f.line_id ASC
    ) AS running_balance
  FROM filtered f
  CROSS JOIN opening o
  ORDER BY f."journalDate" ASC, f."journalId" ASC, f.line_id ASC
  LIMIT $5
)
SELECT
  o.bal AS opening,
  ac.cnt AS activity_count,
  a.line_id,
  a."journalId",
  a."journalNumber",
  a."journalDate",
  a."refNo",
  a."projectCode",
  a.debit,
  a.credit,
  a.running_balance
FROM opening o
CROSS JOIN activity_count ac
LEFT JOIN activity a ON TRUE
"""
