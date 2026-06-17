"use client";
import { useTenantListQuery, invalidateTenantQueries } from "@/lib/api/tenant-query";


import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { FieldSecurityEditor } from "@/components/settings/field-security-editor";
import {
  PermissionMatrix,
} from "@/components/settings/permission-matrix";
import { permissionsFromSet, RolePermissionsEditor } from "@/components/settings/role-permissions-editor";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { rbacApi } from "@/lib/api/tenant";
import { hasPermission, PERM_ROLES_MANAGE } from "@/lib/rbac/permissions";
import { matrixSelectionFromCodes } from "@/lib/rbac/permission-matrix";

type RoleEditorFormProps = {
  mode: "create" | "edit";
  roleId?: string;
};

export function RoleEditorForm({ mode, roleId }: RoleEditorFormProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const returnTo = searchParams.get("returnTo")?.trim() || "";
  const queryClient = useQueryClient();
  const [name, setName] = useState("");
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [strict, setStrict] = useState(false);
  const [description, setDescription] = useState("");
  const [useMatrix, setUseMatrix] = useState(true);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const { data: matrixData } = useTenantListQuery(
    ["permissions-matrix"],
    () => rbacApi.getPermissionsMatrix(),
  );

  const { data: permsData } = useTenantListQuery(["my-permissions"], () => rbacApi.getMyPermissions());
  const canManageRoles = hasPermission(
    permsData?.result?.permissions ?? [],
    PERM_ROLES_MANAGE
  );

  const { data: roleData, isLoading: roleLoading } = useTenantListQuery(["rbac-role", roleId], () => rbacApi.getRole(roleId!),
    { enabled: mode === "edit" && Boolean(roleId) });

  useEffect(() => {
    if (mode !== "edit" || !roleData?.result) return;
    setName(roleData.result.name);
    setDescription(String(roleData.result.description ?? ""));
    const perms = roleData.result.permissions;
    if (Array.isArray(perms)) {
      const codes = perms.map(String);
      if (matrixData?.result) {
        setSelected(matrixSelectionFromCodes(matrixData.result, codes));
      } else {
        setSelected(new Set(codes));
      }
    }
  }, [mode, roleData, matrixData]);

  const saveMutation = useMutation({
    mutationFn: async () => {
      const permissions = permissionsFromSet(selected);
      if (!name.trim()) throw new Error("Role name is required");
      if (permissions.length === 0) throw new Error("Select at least one permission");
      const opts = { strict };
      if (mode === "create") {
        return rbacApi.createRole(
          { name: name.trim(), permissions, description: description.trim() || null },
          opts,
        );
      }
      return rbacApi.updateRole(
        roleId!,
        { name: name.trim(), permissions, description: description.trim() || null },
        opts,
      );
    },
    onSuccess: (res) => {
      const warnings = res.permissionWarnings ?? res.unknownPermissions;
      if (warnings?.length) {
        setMessage(`Saved with warnings: ${warnings.join(", ")}`);
      } else {
        setMessage("Role saved.");
      }
      setError(null);
      void invalidateTenantQueries(queryClient, "rbac-roles");
      if (mode === "create" && returnTo) {
        router.push(returnTo);
        return;
      }
      if (mode === "create" && res.result?.id) {
        router.push(`/settings/roles/${res.result.id}`);
      }
    },
    onError: (e: Error) => setError(e.message),
  });

  const deleteMutation = useMutation({
    mutationFn: () => rbacApi.deleteRole(roleId!),
    onSuccess: () => {
      void invalidateTenantQueries(queryClient, "rbac-roles");
      router.push("/settings/roles");
    },
    onError: (e: Error) => setError(e.message),
  });

  const cloneMutation = useMutation({
    mutationFn: () =>
      rbacApi.cloneRole(
        roleId!,
        { name: `${name.trim() || "Role"} (copy)` },
        { strict }
      ),
    onSuccess: (res) => {
      setMessage("Role cloned.");
      setError(null);
      void invalidateTenantQueries(queryClient, "rbac-roles");
      if (res.result?.id) {
        router.push(`/settings/roles/${res.result.id}`);
      }
    },
    onError: (e: Error) => setError(e.message),
  });

  if (!canManageRoles) {
    return (
      <div>
        <PageHeader title="Roles" breadcrumb="Home / Roles" />
        <p className="text-sm text-fg-muted">
          You need <code>settings.roles.manage</code> to create or edit roles.
        </p>
        <Link href="/settings/roles" className="mt-4 inline-block text-sm text-brand hover:underline">
          Back to roles
        </Link>
      </div>
    );
  }

  const title = mode === "create" ? "New role" : "Edit role";

  return (
    <div>
      <PageHeader
        title={title}
        breadcrumb={`Home / Roles / ${title}`}
        description="Rights tree from the permission catalog (§12.4)."
        actions={
          <Link href="/settings/roles">
            <Button variant="outline">Back to list</Button>
          </Link>
        }
      />

      {error && (
        <div className="mb-4 rounded-md border border-status-danger/30 bg-status-danger/10 px-3 py-2 text-sm text-status-danger">
          {error}
        </div>
      )}
      {message && (
        <div className="mb-4 rounded-md border border-status-success/30 bg-status-success/10 px-3 py-2 text-sm text-status-success">
          {message}
        </div>
      )}

      {mode === "edit" && roleLoading ? (
        <p className="text-sm text-fg-muted">Loading role…</p>
      ) : (
        <form
          className="max-w-3xl rounded-lg border border-border bg-surface p-4"
          onSubmit={(e) => {
            e.preventDefault();
            saveMutation.mutate();
          }}
        >
          <div className="mb-4 space-y-3">
            <label className="block text-sm font-medium text-fg">
              Role name
              <input
                className="mt-1 w-full rounded-md border border-border bg-surface px-3 py-2 text-sm"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={saveMutation.isPending}
              />
            </label>
            <label className="block text-sm font-medium text-fg">
              Description
              <textarea
                className="mt-1 w-full rounded-md border border-border bg-surface px-3 py-2 text-sm"
                rows={2}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                disabled={saveMutation.isPending}
              />
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={strict}
                onChange={(e) => setStrict(e.target.checked)}
              />
              Strict validation (reject unknown permission codes)
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={useMatrix}
                onChange={(e) => setUseMatrix(e.target.checked)}
              />
              Matrix editor (toggle off for legacy checklist)
            </label>
          </div>
          {useMatrix && matrixData?.result ? (
            <PermissionMatrix
              schema={matrixData.result}
              selected={selected}
              onSelectedChange={setSelected}
              disabled={saveMutation.isPending}
            />
          ) : (
            <RolePermissionsEditor
              name={name}
              onNameChange={setName}
              selected={selected}
              onSelectedChange={setSelected}
              strict={strict}
              onStrictChange={setStrict}
              disabled={saveMutation.isPending}
            />
          )}
          {mode === "edit" && roleId && matrixData?.result?.fieldSecurityKeys ? (
            <div className="mt-8 border-t border-border-subtle pt-6">
              <h3 className="mb-3 text-sm font-semibold text-fg">Field security</h3>
              <FieldSecurityEditor
                roleId={roleId}
                fieldKeys={matrixData.result.fieldSecurityKeys}
                accessLevels={matrixData.result.fieldAccessLevels ?? ["view", "edit", "hidden"]}
                disabled={saveMutation.isPending}
                onSaved={() => setMessage("Field security saved.")}
                onError={(msg) => setError(msg)}
              />
            </div>
          ) : null}
          <div className="mt-6 flex flex-wrap gap-2">
            <Button type="submit" disabled={saveMutation.isPending}>
              {saveMutation.isPending ? "Saving…" : "Save role"}
            </Button>
            {mode === "edit" && (
              <>
                <Button
                  type="button"
                  variant="outline"
                  disabled={cloneMutation.isPending}
                  onClick={() => cloneMutation.mutate()}
                >
                  {cloneMutation.isPending ? "Cloning…" : "Clone role"}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  disabled={deleteMutation.isPending}
                  onClick={() => {
                    if (!confirm("Delete this role? Users must be reassigned first.")) return;
                    deleteMutation.mutate();
                  }}
                >
                  Delete role
                </Button>
              </>
            )}
          </div>
        </form>
      )}
    </div>
  );
}
