"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { CollapsibleReportCategory } from "@/components/reports/collapsible-report-category";
import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { rbacApi } from "@/lib/api/tenant";
import { matchText } from "@/lib/list/document-list-filters";

export function togglePermissionCode(
  selected: Set<string>,
  code: string,
): Set<string> {
  if (code === "*") {
    return selected.has("*") ? new Set() : new Set(["*"]);
  }
  const next = new Set(selected);
  next.delete("*");
  if (next.has(code)) next.delete(code);
  else next.add(code);
  return next;
}

export function permissionsFromSet(selected: Set<string>): string[] {
  return Array.from(selected);
}

type RolePermissionsEditorProps = {
  name: string;
  onNameChange: (name: string) => void;
  selected: Set<string>;
  onSelectedChange: (next: Set<string>) => void;
  strict: boolean;
  onStrictChange: (strict: boolean) => void;
  disabled?: boolean;
};

function PermissionCheckboxList({
  permissions,
  selected,
  onSelectedChange,
  disabled,
  fullAccess,
}: {
  permissions: { code: string; label: string }[];
  selected: Set<string>;
  onSelectedChange: (next: Set<string>) => void;
  disabled?: boolean;
  fullAccess: boolean;
}) {
  return (
    <ul className="mt-2 grid gap-2 sm:grid-cols-2">
      {permissions.map((perm) => {
        const checked = selected.has(perm.code);
        return (
          <li key={perm.code}>
            <label className="flex cursor-pointer items-start gap-2 text-sm">
              <input
                type="checkbox"
                className="mt-0.5"
                checked={checked}
                disabled={disabled || (fullAccess && perm.code !== "*")}
                onChange={() => onSelectedChange(togglePermissionCode(selected, perm.code))}
              />
              <span>
                <span className="font-medium text-fg">{perm.label}</span>
                <span className="block font-mono text-xs text-fg-muted">{perm.code}</span>
              </span>
            </label>
          </li>
        );
      })}
    </ul>
  );
}

function selectAllInGroup(selected: Set<string>, codes: string[]): Set<string> {
  const next = new Set(selected);
  next.delete("*");
  for (const code of codes) next.add(code);
  return next;
}

function clearAllInGroup(selected: Set<string>, codes: string[]): Set<string> {
  const next = new Set(selected);
  for (const code of codes) next.delete(code);
  return next;
}

export function RolePermissionsEditor({
  name,
  onNameChange,
  selected,
  onSelectedChange,
  strict,
  onStrictChange,
  disabled,
}: RolePermissionsEditorProps) {
  const [search, setSearch] = useState("");
  const [expandAll, setExpandAll] = useState(true);

  const { data: catalog, isLoading } = useTenantListQuery(["permissions-catalog"], () => rbacApi.getPermissionsCatalog());

  const fullAccess = selected.has("*");

  const filteredGroups = useMemo(() => {
    const q = search.trim().toLowerCase();
    return (catalog?.result ?? [])
      .map((group) => {
        const submodules = (group.submodules ?? [])
          .map((sub) => {
            const permissions = sub.permissions.filter(
              (p) => !q || matchText([p.code, p.label, sub.name, group.group], q),
            );
            return permissions.length ? { ...sub, permissions } : null;
          })
          .filter(Boolean) as typeof group.submodules;

        const permissions = (group.permissions ?? []).filter(
          (p) => !q || matchText([p.code, p.label, group.group], q),
        );

        if (!submodules?.length && !permissions.length) return null;
        return { ...group, submodules, permissions };
      })
      .filter(Boolean) as NonNullable<typeof catalog>["result"];
  }, [catalog?.result, search]);

  return (
    <div className="space-y-6">
      <FormField label="Role name" required>
        <Input
          value={name}
          disabled={disabled}
          onChange={(e) => onNameChange(e.target.value)}
          placeholder="e.g. Sales clerk"
        />
      </FormField>

      <label className="flex items-center gap-2 text-sm text-fg">
        <input
          type="checkbox"
          checked={strict}
          disabled={disabled}
          onChange={(e) => onStrictChange(e.target.checked)}
        />
        Strict validation (reject unknown permission codes on save)
      </label>

      <div>
        <div className="mb-3 flex flex-wrap items-center gap-3">
          <h3 className="text-sm font-semibold text-fg">Permissions</h3>
          <div className="max-w-xs flex-1">
            <Input
              type="search"
              placeholder="Search permissions…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              aria-label="Search permissions"
            />
          </div>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => setExpandAll((v) => !v)}
          >
            {expandAll ? "Collapse all" : "Expand all"}
          </Button>
        </div>

        {isLoading && <p className="text-sm text-fg-muted">Loading catalog…</p>}
        {fullAccess && (
          <p className="mb-3 text-sm text-brand">
            Full access (<code>*</code>) is selected; other codes are ignored.
          </p>
        )}

        <div className="space-y-3">
          {filteredGroups.map((group) => {
            const groupCodes = [
              ...group.permissions.map((p) => p.code),
              ...(group.submodules ?? []).flatMap((s) => s.permissions.map((p) => p.code)),
            ];
            return (
              <CollapsibleReportCategory
                key={group.group}
                title={group.group}
                count={groupCodes.length}
                defaultOpen={expandAll}
              >
                <div className="border-b border-border px-4 py-2">
                  <div className="flex flex-wrap gap-2">
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      disabled={disabled || fullAccess}
                      onClick={() =>
                        onSelectedChange(selectAllInGroup(selected, groupCodes))
                      }
                    >
                      Select all in {group.group}
                    </Button>
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      disabled={disabled}
                      onClick={() =>
                        onSelectedChange(clearAllInGroup(selected, groupCodes))
                      }
                    >
                      Clear {group.group}
                    </Button>
                  </div>
                </div>
                {group.submodules && group.submodules.length > 0 ? (
                  <div className="space-y-4 px-4 py-3">
                    {group.submodules.map((sub) => (
                      <div key={`${group.group}-${sub.name}`}>
                        <h4 className="text-xs font-medium text-fg">{sub.name}</h4>
                        <PermissionCheckboxList
                          permissions={sub.permissions}
                          selected={selected}
                          onSelectedChange={onSelectedChange}
                          disabled={disabled}
                          fullAccess={fullAccess}
                        />
                      </div>
                    ))}
                  </div>
                ) : null}
                {group.permissions.length > 0 ? (
                  <div className="px-4 py-3">
                    <PermissionCheckboxList
                      permissions={group.permissions}
                      selected={selected}
                      onSelectedChange={onSelectedChange}
                      disabled={disabled}
                      fullAccess={fullAccess}
                    />
                  </div>
                ) : null}
              </CollapsibleReportCategory>
            );
          })}
          {!isLoading && filteredGroups.length === 0 && (
            <p className="text-sm text-fg-muted">No permissions match your search.</p>
          )}
        </div>
      </div>
    </div>
  );
}
