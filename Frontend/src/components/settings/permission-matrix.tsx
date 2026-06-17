"use client";

import { useMemo, useState } from "react";

import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";
import {
  clearMatrixColumn,
  grantMatrixColumn,
  isMatrixCellGranted,
  toggleMatrixCell,
  type PermissionMatrixSchema,
} from "@/lib/rbac/permission-matrix";

type PermissionMatrixProps = {
  schema: PermissionMatrixSchema;
  selected: Set<string>;
  onSelectedChange: (next: Set<string>) => void;
  disabled?: boolean;
};

const ACTION_LABELS: Record<string, string> = {
  view: "View",
  create: "Create",
  edit: "Edit",
  delete: "Delete",
  approve: "Approve",
  export: "Export",
  print: "Print",
  import: "Import",
  void: "Void",
  manage_settings: "Settings",
  manage_users: "Users",
  manage_roles: "Roles",
  api_access: "API",
};

export function PermissionMatrix({
  schema,
  selected,
  onSelectedChange,
  disabled,
}: PermissionMatrixProps) {
  const [search, setSearch] = useState("");
  const fullAccess = selected.has("*");

  const visibleModules = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return schema.modules;
    return schema.modules
      .map((mod) => ({
        ...mod,
        resources: mod.resources.filter(
          (r) =>
            r.label.toLowerCase().includes(q) ||
            mod.moduleLabel.toLowerCase().includes(q),
        ),
      }))
      .filter((mod) => mod.resources.length > 0);
  }, [schema.modules, search]);

  return (
    <div className="space-y-3">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <Input
          type="search"
          placeholder="Search permissions…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="max-w-xs"
          disabled={disabled}
        />
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={fullAccess}
            disabled={disabled}
            onChange={() =>
              onSelectedChange(fullAccess ? new Set() : new Set(["*"]))
            }
          />
          Full access (Super Admin)
        </label>
      </div>

      <div className="overflow-x-auto rounded-lg border border-border/60">
        <table className="min-w-full text-sm">
          <thead className="bg-surface-elevated/80 text-left text-xs uppercase tracking-wide text-fg-muted">
            <tr>
              <th className="sticky left-0 z-10 min-w-[8rem] bg-surface-elevated/95 px-3 py-2">
                Module
              </th>
              <th className="sticky left-[8rem] z-10 min-w-[9rem] bg-surface-elevated/95 px-3 py-2">
                Resource
              </th>
              {schema.actions.map((action) => (
                <th key={action} className="px-2 py-2 text-center whitespace-nowrap">
                  {ACTION_LABELS[action] ?? action}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {visibleModules.map((mod) =>
              mod.resources.map((res, idx) => (
                <tr
                  key={`${mod.module}-${res.resource}`}
                  className="border-t border-border-subtle/60 odd:bg-surface/40"
                >
                  {idx === 0 ? (
                    <td
                      rowSpan={mod.resources.length}
                      className="sticky left-0 z-[1] bg-surface px-3 py-2 align-top font-medium"
                    >
                      {mod.moduleLabel}
                      <div className="mt-2 flex flex-wrap gap-1">
                        {schema.actions.map((action) => (
                          <button
                            key={action}
                            type="button"
                            className="text-[10px] text-brand hover:underline disabled:opacity-50"
                            disabled={disabled || fullAccess}
                            onClick={() =>
                              onSelectedChange(
                                grantMatrixColumn(mod, selected, action),
                              )
                            }
                          >
                            All {ACTION_LABELS[action] ?? action}
                          </button>
                        ))}
                      </div>
                    </td>
                  ) : null}
                  <td className="sticky left-[8rem] z-[1] bg-surface px-3 py-2 font-medium">
                    {res.label}
                  </td>
                  {schema.actions.map((action) => {
                    const code = res.actions[action];
                    const checked = isMatrixCellGranted(selected, code);
                    return (
                      <td key={action} className="px-2 py-2 text-center">
                        {code ? (
                          <input
                            type="checkbox"
                            className={cn("h-4 w-4", disabled && "opacity-50")}
                            checked={checked}
                            disabled={disabled || fullAccess}
                            aria-label={`${res.label} ${ACTION_LABELS[action] ?? action}`}
                            onChange={() =>
                              onSelectedChange(toggleMatrixCell(selected, code))
                            }
                          />
                        ) : (
                          <span className="text-fg-muted">—</span>
                        )}
                      </td>
                    );
                  })}
                </tr>
              )),
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
