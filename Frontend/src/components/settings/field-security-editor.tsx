"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { accessControlApi } from "@/lib/api/tenant";

type FieldKey = { key: string; label: string };

type FieldSecurityEditorProps = {
  roleId: string;
  fieldKeys: FieldKey[];
  accessLevels: string[];
  disabled?: boolean;
  onSaved?: () => void;
  onError?: (message: string) => void;
};

const LEVEL_LABELS: Record<string, string> = {
  edit: "Edit",
  view: "View only",
  hidden: "Hidden",
};

export function FieldSecurityEditor({
  roleId,
  fieldKeys,
  accessLevels,
  disabled,
  onSaved,
  onError,
}: FieldSecurityEditorProps) {
  const levels = accessLevels.length ? accessLevels : ["view", "edit", "hidden"];
  const [levelsByKey, setLevelsByKey] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    void accessControlApi.listFieldSecurity(roleId).then(
      (res) => {
        if (cancelled) return;
        const next: Record<string, string> = {};
        for (const row of res.result ?? []) {
          next[row.fieldKey] = row.accessLevel;
        }
        setLevelsByKey(next);
        setLoading(false);
      },
      () => {
        if (!cancelled) setLoading(false);
      },
    );
    return () => {
      cancelled = true;
    };
  }, [roleId]);

  async function save() {
    setSaving(true);
    try {
      const policies = fieldKeys
        .map((field) => ({
          fieldKey: field.key,
          accessLevel: levelsByKey[field.key] ?? "edit",
        }))
        .filter((p) => p.accessLevel !== "edit");
      await accessControlApi.replaceFieldSecurity({ roleId, policies });
      onSaved?.();
    } catch (err) {
      onError?.(err instanceof Error ? err.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return <p className="text-sm text-fg-muted">Loading field security…</p>;
  }

  return (
    <div className="space-y-3">
      <p className="text-sm text-fg-muted">
        Restrict sensitive fields for users with this role. Unlisted fields default to full edit access.
      </p>
      <div className="overflow-x-auto rounded-md border border-border/60">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="border-b border-border-subtle bg-surface-elevated/50">
              <th className="px-3 py-2 text-left font-medium">Field</th>
              {levels.map((level) => (
                <th key={level} className="px-3 py-2 text-center font-medium">
                  {LEVEL_LABELS[level] ?? level}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {fieldKeys.map((field) => (
              <tr key={field.key} className="border-b border-border-subtle last:border-0">
                <td className="px-3 py-2">{field.label}</td>
                {levels.map((level) => (
                  <td key={level} className="px-3 py-2 text-center">
                    <input
                      type="radio"
                      name={`field-${field.key}`}
                      checked={(levelsByKey[field.key] ?? "edit") === level}
                      disabled={disabled || saving}
                      onChange={() =>
                        setLevelsByKey((prev) => ({ ...prev, [field.key]: level }))
                      }
                      aria-label={`${field.label} — ${LEVEL_LABELS[level] ?? level}`}
                    />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {!disabled ? (
        <Button type="button" size="sm" disabled={saving} onClick={() => void save()}>
          {saving ? "Saving…" : "Save field security"}
        </Button>
      ) : null}
    </div>
  );
}
