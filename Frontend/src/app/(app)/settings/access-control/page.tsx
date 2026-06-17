"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { FieldSecurityEditor } from "@/components/settings/field-security-editor";
import { DataScopeEditor } from "@/components/settings/data-scope-editor";
import { PermissionMatrix } from "@/components/settings/permission-matrix";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { Select } from "@/components/ui/select";
import { MotionFade } from "@/components/ui/motion-fade";
import { useToast } from "@/components/ui/toast";
import { accessControlApi, inventoryApi, partiesApi, rbacApi, type ModuleAccessRow } from "@/lib/api/tenant";
import { useTenantListQuery, useTenantReferenceQuery, invalidateTenantQueries } from "@/lib/api/tenant-query";
import { Can, usePermission } from "@/lib/rbac/can";
import { PERM_ACCESS_CONTROL_MANAGE, PERM_ROLES_MANAGE } from "@/lib/rbac/permissions";
import { cn } from "@/lib/utils";

const TABS = [
  { id: "modules", label: "Modules" },
  { id: "roles", label: "Roles" },
  { id: "matrix", label: "Permission matrix" },
  { id: "field-security", label: "Field security" },
  { id: "data-scope", label: "Data scope" },
  { id: "approvals", label: "Approvals" },
  { id: "audit", label: "Audit log" },
] as const;

function SeedTemplatesButton() {
  const queryClient = useQueryClient();
  const toast = useToast();
  const seed = useMutation({
    mutationFn: () => rbacApi.seedMissingRoleTemplates(),
    onSuccess: (res) => {
      void invalidateTenantQueries(queryClient, "rbac-roles");
      const count = res.result?.length ?? 0;
      if (count === 0) {
        toast.success("All default role templates are already present.");
      } else {
        toast.success(`Added ${count} missing role template(s).`);
      }
    },
    onError: (err: Error) => toast.error(err.message),
  });
  return (
    <Button
      type="button"
      variant="outline"
      disabled={seed.isPending}
      onClick={() => seed.mutate()}
    >
      {seed.isPending ? "Seeding…" : "Seed missing templates"}
    </Button>
  );
}

function RolePicker({
  roles,
  value,
  onChange,
}: {
  roles: { id: string; name: string }[];
  value: string;
  onChange: (id: string) => void;
}) {
  return (
    <Select value={value} onChange={(e) => onChange(e.target.value)}>
      <option value="">Select a role…</option>
      {roles.map((role) => (
        <option key={role.id} value={role.id}>
          {role.name}
        </option>
      ))}
    </Select>
  );
}

function MatrixTab({
  roles,
  canManage,
}: {
  roles: { id: string; name: string; permissions?: string[] }[];
  canManage: boolean;
}) {
  const queryClient = useQueryClient();
  const toast = useToast();
  const [roleId, setRoleId] = useState("");
  const { data: matrixSchema } = useTenantReferenceQuery(
    ["permissions-matrix"],
    () => rbacApi.getPermissionsMatrix(),
  );
  const selectedRole = roles.find((r) => r.id === roleId);
  const [selected, setSelected] = useState<Set<string>>(new Set());

  useEffect(() => {
    setSelected(new Set(selectedRole?.permissions ?? []));
  }, [selectedRole?.id, selectedRole?.permissions]);

  const save = useMutation({
    mutationFn: () =>
      rbacApi.updateRole(roleId, { permissions: Array.from(selected) }),
    onSuccess: () => {
      void invalidateTenantQueries(queryClient, "rbac-roles");
      toast.success("Permissions saved.");
    },
    onError: (err: Error) => toast.error(err.message),
  });

  const schema = matrixSchema?.result;
  if (!schema) {
    return <p className="text-sm text-fg-muted">Loading matrix…</p>;
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-3">
        <RolePicker roles={roles} value={roleId} onChange={setRoleId} />
        {canManage && roleId ? (
          <Button
            type="button"
            disabled={save.isPending}
            onClick={() => save.mutate()}
          >
            {save.isPending ? "Saving…" : "Save permissions"}
          </Button>
        ) : null}
      </div>
      <PermissionMatrix
        schema={schema}
        selected={selected}
        onSelectedChange={setSelected}
        disabled={!canManage || !roleId}
      />
    </div>
  );
}

function FieldSecurityTab({
  roles,
  canManage,
}: {
  roles: { id: string; name: string }[];
  canManage: boolean;
}) {
  const toast = useToast();
  const [roleId, setRoleId] = useState("");
  const { data: matrixSchema } = useTenantReferenceQuery(
    ["permissions-matrix"],
    () => rbacApi.getPermissionsMatrix(),
  );
  const fieldKeys = matrixSchema?.result?.fieldSecurityKeys ?? [];
  const accessLevels = matrixSchema?.result?.fieldAccessLevels ?? [];

  return (
    <div className="space-y-3">
      <RolePicker roles={roles} value={roleId} onChange={setRoleId} />
      {!roleId ? (
        <p className="text-sm text-fg-muted">Select a role to configure field security.</p>
      ) : (
        <FieldSecurityEditor
          roleId={roleId}
          fieldKeys={fieldKeys}
          accessLevels={accessLevels}
          disabled={!canManage}
          onSaved={() => toast.success("Field security saved.")}
          onError={(message) => toast.error(message)}
        />
      )}
    </div>
  );
}

function DataScopeTab({
  canManage,
}: {
  canManage: boolean;
}) {
  const { data: usersData } = useTenantListQuery(["rbac-users-ref"], () =>
    rbacApi.listUsers({ page: 1, pageSize: 200 }),
  );
  const { data: customersData } = useTenantReferenceQuery(["customers-ref"], () =>
    partiesApi.listCustomers(),
  );
  const { data: suppliersData } = useTenantReferenceQuery(["suppliers-ref"], () =>
    partiesApi.listSuppliers(),
  );
  const { data: productsData } = useTenantReferenceQuery(["products-ref"], () =>
    inventoryApi.listProducts(),
  );

  const members = (usersData?.result?.items ?? []).map((row) => {
    const name = `${row.firstName ?? ""} ${row.lastName ?? ""}`.trim();
    return {
      membershipId: String(row.id),
      label: name || row.email || "User",
    };
  });
  const customers = customersData?.result ?? [];
  const suppliers = suppliersData?.result ?? [];
  const products = productsData?.result ?? [];

  return (
    <DataScopeEditor
      members={members}
      disabled={!canManage}
      customerHint={customers.slice(0, 3).map((c) => c.code).join(", ") || undefined}
      supplierHint={suppliers.slice(0, 3).map((s) => s.code).join(", ") || undefined}
      productHint={products.slice(0, 3).map((p) => p.code).join(", ") || undefined}
    />
  );
}

export default function AccessControlPage() {
  const [tab, setTab] = useState<(typeof TABS)[number]["id"]>("modules");
  const queryClient = useQueryClient();
  const toast = useToast();
  const canManage = usePermission(PERM_ACCESS_CONTROL_MANAGE);
  const canManageRoles = usePermission(PERM_ROLES_MANAGE);
  const canEditRbac = canManage || canManageRoles;

  const { data: modulesData, isLoading: modulesLoading } = useTenantReferenceQuery(
    ["access-control-modules"],
    () => accessControlApi.listModules(),
  );
  const { data: rolesData } = useTenantListQuery(["rbac-roles"], () => rbacApi.listRoles());
  const roles = rolesData?.result ?? [];
  const [draftModules, setDraftModules] = useState<ModuleAccessRow[] | null>(null);
  const modules = draftModules ?? modulesData?.result ?? [];

  const saveModules = useMutation({
    mutationFn: () => accessControlApi.replaceModules(modules),
    onSuccess: () => {
      setDraftModules(null);
      void invalidateTenantQueries(queryClient, "access-control-modules");
      void invalidateTenantQueries(queryClient, "my-permissions");
      toast.success("Module settings saved.");
    },
    onError: (err: Error) => toast.error(err.message),
  });

  return (
    <div>
      <PageHeader
        title="Access control"
        breadcrumb="Settings / Access control"
        description="Manage modules, roles, permissions, field security, and data scope."
      />

      <div className="mb-4 flex flex-wrap gap-2 border-b border-border-subtle pb-2">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => setTab(t.id)}
            className={cn(
              "rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
              tab === t.id
                ? "bg-brand-600 text-on-brand"
                : "text-fg-muted hover:bg-surface-elevated hover:text-fg",
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      <MotionFade key={tab}>
      {tab === "modules" && (
        <section className="space-y-4">
          <p className="text-sm text-fg-muted">
            Disable modules globally to hide sidebar items, block routes, and remove related permissions.
          </p>
          {modulesLoading ? (
            <p className="text-sm text-fg-muted">Loading modules…</p>
          ) : (
            <ul className="divide-y divide-border-subtle rounded-lg border border-border/60">
              {modules.map((m) => (
                <li
                  key={m.moduleCode}
                  className="flex flex-wrap items-center justify-between gap-3 px-3 py-2.5"
                >
                  <span className="font-medium capitalize">{m.moduleCode}</span>
                  <div className="flex flex-wrap gap-4 text-sm">
                    {(
                      [
                        ["enabled", "Enabled"],
                        ["sidebarVisible", "Sidebar"],
                        ["routesEnabled", "Routes"],
                        ["apiEnabled", "APIs"],
                        ["reportsEnabled", "Reports"],
                        ["widgetsEnabled", "Widgets"],
                      ] as const
                    ).map(([key, label]) => (
                      <label key={key} className="flex items-center gap-1.5">
                        <input
                          type="checkbox"
                          checked={Boolean(m[key])}
                          disabled={!canManage}
                          onChange={(e) => {
                            setDraftModules(
                              modules.map((row) =>
                                row.moduleCode === m.moduleCode
                                  ? { ...row, [key]: e.target.checked }
                                  : row,
                              ),
                            );
                          }}
                        />
                        {label}
                      </label>
                    ))}
                  </div>
                </li>
              ))}
            </ul>
          )}
          <Can permission={PERM_ACCESS_CONTROL_MANAGE}>
            <Button
              type="button"
              disabled={saveModules.isPending || draftModules === null}
              onClick={() => saveModules.mutate()}
            >
              Save module settings
            </Button>
          </Can>
        </section>
      )}

      {tab === "roles" && (
        <section className="space-y-3">
          <div className="flex flex-wrap gap-2">
            <Can permission={PERM_ROLES_MANAGE}>
              <Button asChild>
                <Link href="/settings/roles/new">New role</Link>
              </Button>
            </Can>
            <Can permission={PERM_ROLES_MANAGE}>
              <SeedTemplatesButton />
            </Can>
            <Button asChild variant="outline">
              <Link href="/settings/roles">All roles</Link>
            </Button>
          </div>
          <ul className="divide-y divide-border-subtle rounded-lg border border-border/60">
            {(rolesData?.result ?? []).map((role) => (
              <li key={role.id} className="flex items-center justify-between px-3 py-2">
                <div>
                  <div className="font-medium">{role.name}</div>
                  {role.description ? (
                    <div className="text-xs text-fg-muted">{role.description}</div>
                  ) : null}
                </div>
                <Button asChild size="sm" variant="outline">
                  <Link href={`/settings/roles/${role.id}`}>Edit</Link>
                </Button>
              </li>
            ))}
          </ul>
        </section>
      )}

      {tab === "matrix" && (
        <section>
          <p className="mb-3 text-sm text-fg-muted">
            Select a role to view or edit its permission matrix.
          </p>
          <MatrixTab roles={roles} canManage={canEditRbac} />
        </section>
      )}

      {tab === "field-security" && (
        <section className="space-y-3">
          <p className="text-sm text-fg-muted">
            Control which sensitive fields each role can view or edit.
          </p>
          <FieldSecurityTab roles={roles} canManage={canEditRbac} />
        </section>
      )}

      {tab === "data-scope" && (
        <section className="space-y-3">
          <p className="text-sm text-fg-muted">
            Assign customers, suppliers, and products per user membership.
          </p>
          <DataScopeTab canManage={canEditRbac} />
        </section>
      )}

      {tab === "approvals" && (
        <section className="space-y-2 text-sm text-fg-muted">
          <p>Configure approval thresholds and approver roles.</p>
          <Button asChild variant="outline">
            <Link href="/settings/authorisation">Approval policies</Link>
          </Button>
        </section>
      )}

      {tab === "audit" && (
        <section className="space-y-2 text-sm text-fg-muted">
          <Button asChild variant="outline">
            <Link href="/settings/user-log?rbacOnly=1">View RBAC audit log</Link>
          </Button>
        </section>
      )}
      </MotionFade>
    </div>
  );
}
