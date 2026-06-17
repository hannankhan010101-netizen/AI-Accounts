-- Seed Standard User and User roles for companies that only have Administrator (§12.3)

INSERT INTO roles (id, company_id, name, permissions, created_at, updated_at)
SELECT
  'seed_std_' || c.id,
  c.id,
  'Standard User',
  '["sales.read","purchases.read","inventory.read","reports.read","settings.users.read"]'::jsonb,
  CURRENT_TIMESTAMP,
  CURRENT_TIMESTAMP
FROM "Company" c
WHERE NOT EXISTS (
  SELECT 1 FROM roles r
  WHERE r.company_id = c.id AND r.name = 'Standard User'
);

INSERT INTO roles (id, company_id, name, permissions, created_at, updated_at)
SELECT
  'seed_user_' || c.id,
  c.id,
  'User',
  '["sales.read","purchases.read","inventory.read","reports.read","settings.users.read","settings.users.invite","sales.invoices.create","purchases.bills.create"]'::jsonb,
  CURRENT_TIMESTAMP,
  CURRENT_TIMESTAMP
FROM "Company" c
WHERE NOT EXISTS (
  SELECT 1 FROM roles r
  WHERE r.company_id = c.id AND r.name = 'User'
);
