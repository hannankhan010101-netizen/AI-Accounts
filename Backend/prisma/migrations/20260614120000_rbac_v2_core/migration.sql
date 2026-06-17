-- RBAC v2: normalized permissions, multi-role, module config, field security, data scope.

-- Extend roles
ALTER TABLE "roles" ADD COLUMN IF NOT EXISTS "code" TEXT;
ALTER TABLE "roles" ADD COLUMN IF NOT EXISTS "description" TEXT;
ALTER TABLE "roles" ADD COLUMN IF NOT EXISTS "parent_role_id" TEXT;
ALTER TABLE "roles" ADD COLUMN IF NOT EXISTS "is_system" BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE "roles" ADD COLUMN IF NOT EXISTS "is_template" BOOLEAN NOT NULL DEFAULT false;
ALTER TABLE "roles" ADD COLUMN IF NOT EXISTS "sort_order" INT NOT NULL DEFAULT 0;

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'roles_parent_role_id_fkey'
  ) THEN
    ALTER TABLE "roles"
      ADD CONSTRAINT "roles_parent_role_id_fkey"
      FOREIGN KEY ("parent_role_id") REFERENCES "roles"("id") ON DELETE SET NULL ON UPDATE CASCADE;
  END IF;
END $$;

CREATE UNIQUE INDEX IF NOT EXISTS "roles_company_id_code_key"
  ON "roles"("company_id", "code") WHERE "code" IS NOT NULL;

CREATE INDEX IF NOT EXISTS "roles_company_id_parent_role_id_idx"
  ON "roles"("company_id", "parent_role_id");

-- Permission catalog
CREATE TABLE IF NOT EXISTS "permission_definitions" (
    "code" TEXT NOT NULL,
    "module" TEXT NOT NULL,
    "resource" TEXT NOT NULL,
    "action" TEXT NOT NULL,
    "label" TEXT NOT NULL,
    "group_label" TEXT,
    "sort_order" INT NOT NULL DEFAULT 0,
    CONSTRAINT "permission_definitions_pkey" PRIMARY KEY ("code")
);

CREATE INDEX IF NOT EXISTS "permission_definitions_module_resource_idx"
  ON "permission_definitions"("module", "resource");

-- Role grants
CREATE TABLE IF NOT EXISTS "role_permissions" (
    "role_id" TEXT NOT NULL,
    "permission_code" TEXT NOT NULL,
    "granted" BOOLEAN NOT NULL DEFAULT true,
    CONSTRAINT "role_permissions_pkey" PRIMARY KEY ("role_id", "permission_code")
);

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'role_permissions_role_id_fkey') THEN
    ALTER TABLE "role_permissions"
      ADD CONSTRAINT "role_permissions_role_id_fkey"
      FOREIGN KEY ("role_id") REFERENCES "roles"("id") ON DELETE CASCADE ON UPDATE CASCADE;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'role_permissions_permission_code_fkey') THEN
    ALTER TABLE "role_permissions"
      ADD CONSTRAINT "role_permissions_permission_code_fkey"
      FOREIGN KEY ("permission_code") REFERENCES "permission_definitions"("code") ON DELETE CASCADE ON UPDATE CASCADE;
  END IF;
END $$;

-- Multi-role
CREATE TABLE IF NOT EXISTS "membership_roles" (
    "membership_id" TEXT NOT NULL,
    "role_id" TEXT NOT NULL,
    "is_primary" BOOLEAN NOT NULL DEFAULT false,
    CONSTRAINT "membership_roles_pkey" PRIMARY KEY ("membership_id", "role_id")
);

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'membership_roles_membership_id_fkey') THEN
    ALTER TABLE "membership_roles"
      ADD CONSTRAINT "membership_roles_membership_id_fkey"
      FOREIGN KEY ("membership_id") REFERENCES "company_memberships"("id") ON DELETE CASCADE ON UPDATE CASCADE;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'membership_roles_role_id_fkey') THEN
    ALTER TABLE "membership_roles"
      ADD CONSTRAINT "membership_roles_role_id_fkey"
      FOREIGN KEY ("role_id") REFERENCES "roles"("id") ON DELETE CASCADE ON UPDATE CASCADE;
  END IF;
END $$;

CREATE INDEX IF NOT EXISTS "membership_roles_role_id_idx" ON "membership_roles"("role_id");

-- Module access control
CREATE TABLE IF NOT EXISTS "company_module_config" (
    "company_id" TEXT NOT NULL,
    "module_code" TEXT NOT NULL,
    "enabled" BOOLEAN NOT NULL DEFAULT true,
    "sidebar_visible" BOOLEAN NOT NULL DEFAULT true,
    "routes_enabled" BOOLEAN NOT NULL DEFAULT true,
    "api_enabled" BOOLEAN NOT NULL DEFAULT true,
    "reports_enabled" BOOLEAN NOT NULL DEFAULT true,
    "widgets_enabled" BOOLEAN NOT NULL DEFAULT true,
    CONSTRAINT "company_module_config_pkey" PRIMARY KEY ("company_id", "module_code")
);

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'company_module_config_company_id_fkey') THEN
    ALTER TABLE "company_module_config"
      ADD CONSTRAINT "company_module_config_company_id_fkey"
      FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;
  END IF;
END $$;

-- Field-level security
CREATE TABLE IF NOT EXISTS "field_security_policies" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "role_id" TEXT NOT NULL,
    "field_key" TEXT NOT NULL,
    "access_level" TEXT NOT NULL,
    CONSTRAINT "field_security_policies_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX IF NOT EXISTS "field_security_policies_company_role_field_key"
  ON "field_security_policies"("company_id", "role_id", "field_key");

CREATE INDEX IF NOT EXISTS "field_security_policies_role_id_idx"
  ON "field_security_policies"("role_id");

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'field_security_policies_company_id_fkey') THEN
    ALTER TABLE "field_security_policies"
      ADD CONSTRAINT "field_security_policies_company_id_fkey"
      FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'field_security_policies_role_id_fkey') THEN
    ALTER TABLE "field_security_policies"
      ADD CONSTRAINT "field_security_policies_role_id_fkey"
      FOREIGN KEY ("role_id") REFERENCES "roles"("id") ON DELETE CASCADE ON UPDATE CASCADE;
  END IF;
END $$;

-- Data scope assignments
CREATE TABLE IF NOT EXISTS "user_data_assignments" (
    "id" TEXT NOT NULL,
    "company_id" TEXT NOT NULL,
    "membership_id" TEXT NOT NULL,
    "scope_type" TEXT NOT NULL,
    "scope_id" TEXT NOT NULL,
    CONSTRAINT "user_data_assignments_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX IF NOT EXISTS "user_data_assignments_membership_scope_key"
  ON "user_data_assignments"("membership_id", "scope_type", "scope_id");

CREATE INDEX IF NOT EXISTS "user_data_assignments_membership_id_idx"
  ON "user_data_assignments"("membership_id");

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'user_data_assignments_company_id_fkey') THEN
    ALTER TABLE "user_data_assignments"
      ADD CONSTRAINT "user_data_assignments_company_id_fkey"
      FOREIGN KEY ("company_id") REFERENCES "Company"("id") ON DELETE CASCADE ON UPDATE CASCADE;
  END IF;
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'user_data_assignments_membership_id_fkey') THEN
    ALTER TABLE "user_data_assignments"
      ADD CONSTRAINT "user_data_assignments_membership_id_fkey"
      FOREIGN KEY ("membership_id") REFERENCES "company_memberships"("id") ON DELETE CASCADE ON UPDATE CASCADE;
  END IF;
END $$;

-- Migrate legacy Administrator role
UPDATE "roles"
SET
  "code" = 'super_admin',
  "is_system" = true,
  "name" = CASE WHEN "name" = 'Administrator' THEN 'Super Admin' ELSE "name" END,
  "description" = COALESCE("description", 'Full tenant control')
WHERE "name" = 'Administrator' AND "code" IS NULL;

-- Backfill membership_roles from primary roleId
INSERT INTO "membership_roles" ("membership_id", "role_id", "is_primary")
SELECT cm."id", cm."role_id", true
FROM "company_memberships" cm
WHERE cm."role_id" IS NOT NULL
ON CONFLICT DO NOTHING;
