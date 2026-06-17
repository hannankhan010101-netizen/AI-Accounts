"use client";

import { useEffect, useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { rbacApi, type RbacRole } from "@/lib/api/tenant";

type MultiRoleSelectProps = {
  userId: string;
  roleIds: string[];
  roles: RbacRole[];
  disabled?: boolean;
  onSaved: () => void;
  onError: (message: string) => void;
};

function roleLabel(roles: RbacRole[], roleId: string): string {
  return roles.find((r) => r.id === roleId)?.name ?? roleId;
}

export function MultiRoleSelect({
  userId,
  roleIds,
  roles,
  disabled,
  onSaved,
  onError,
}: MultiRoleSelectProps) {
  const [open, setOpen] = useState(false);
  const [selected, setSelected] = useState<string[]>(roleIds);
  const [primaryRoleId, setPrimaryRoleId] = useState(roleIds[0] ?? "");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    setSelected(roleIds);
    setPrimaryRoleId(roleIds[0] ?? "");
  }, [roleIds]);

  const summary = useMemo(() => {
    if (selected.length === 0) return "No roles";
    const names = selected.map((id) => roleLabel(roles, id));
    if (names.length <= 2) return names.join(", ");
    return `${names.slice(0, 2).join(", ")} +${names.length - 2}`;
  }, [roles, selected]);

  async function save() {
    if (selected.length === 0) {
      onError("Select at least one role");
      return;
    }
    const primary = selected.includes(primaryRoleId) ? primaryRoleId : selected[0];
    setSaving(true);
    try {
      await rbacApi.assignUserRoles(userId, {
        roleIds: selected,
        primaryRoleId: primary,
      });
      setOpen(false);
      onSaved();
    } catch (err) {
      onError(err instanceof Error ? err.message : "Assign failed");
    } finally {
      setSaving(false);
    }
  }

  function toggleRole(roleId: string, checked: boolean) {
    setSelected((prev) => {
      if (checked) {
        const next = prev.includes(roleId) ? prev : [...prev, roleId];
        if (!primaryRoleId || !next.includes(primaryRoleId)) {
          setPrimaryRoleId(roleId);
        }
        return next;
      }
      const next = prev.filter((id) => id !== roleId);
      if (primaryRoleId === roleId) {
        setPrimaryRoleId(next[0] ?? "");
      }
      return next;
    });
  }

  if (disabled) {
    return <span className="text-sm">{summary}</span>;
  }

  return (
    <div className="relative min-w-[10rem]">
      <button
        type="button"
        className="flex w-full items-center justify-between gap-2 rounded-md border border-border bg-surface px-2 py-1.5 text-left text-sm hover:bg-surface-elevated"
        onClick={() => setOpen((v) => !v)}
      >
        <span className="truncate">{summary}</span>
        {selected.length > 1 ? (
          <Badge variant="outline" className="shrink-0">
            {selected.length}
          </Badge>
        ) : null}
      </button>
      {open ? (
        <div className="absolute z-20 mt-1 w-56 rounded-md border border-border bg-surface p-2 shadow-lg">
          <ul className="max-h-48 space-y-1 overflow-y-auto">
            {roles.map((role) => {
              const checked = selected.includes(role.id);
              return (
                <li key={role.id} className="flex items-center gap-2 text-sm">
                  <Checkbox
                    checked={checked}
                    onChange={(e) => toggleRole(role.id, e.target.checked)}
                    aria-label={role.name}
                  />
                  <span className="min-w-0 flex-1 truncate">{role.name}</span>
                  {checked && selected.length > 1 ? (
                    <label className="flex items-center gap-1 text-xs text-fg-muted">
                      <input
                        type="radio"
                        name={`primary-${userId}`}
                        checked={primaryRoleId === role.id}
                        onChange={() => setPrimaryRoleId(role.id)}
                      />
                      Primary
                    </label>
                  ) : null}
                </li>
              );
            })}
          </ul>
          <div className="mt-2 flex justify-end gap-2 border-t border-border-subtle pt-2">
            <Button type="button" size="sm" variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button type="button" size="sm" disabled={saving} onClick={() => void save()}>
              {saving ? "Saving…" : "Save"}
            </Button>
          </div>
        </div>
      ) : null}
    </div>
  );
}
