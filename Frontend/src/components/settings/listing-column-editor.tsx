"use client";

import { useMemo } from "react";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import type { ListingColumnSetting } from "@/lib/api/tenant";

interface ListingColumnEditorProps {
  columns: ListingColumnSetting[];
  onChange: (next: ListingColumnSetting[]) => void;
  onSave: () => void;
  onReset: () => void;
  saving?: boolean;
}

export function ListingColumnEditor({
  columns,
  onChange,
  onSave,
  onReset,
  saving,
}: ListingColumnEditorProps) {
  const sorted = useMemo(
    () => [...columns].sort((a, b) => a.order - b.order),
    [columns],
  );

  function move(index: number, dir: -1 | 1) {
    const next = [...sorted];
    const target = index + dir;
    if (target < 0 || target >= next.length) return;
    const tmp = next[index].order;
    next[index] = { ...next[index], order: next[target].order };
    next[target] = { ...next[target], order: tmp };
    onChange(next);
  }

  function patchRow(index: number, partial: Partial<ListingColumnSetting>) {
    const next = sorted.map((c, i) => (i === index ? { ...c, ...partial } : c));
    onChange(next);
  }

  return (
    <section className="rounded-lg border border-border bg-surface">
      <div className="flex flex-wrap gap-2 border-b border-border px-4 py-3">
        <Button type="button" variant="outline" onClick={onReset}>
          Reset
        </Button>
        <Button type="button" disabled={saving} onClick={onSave}>
          {saving ? "Updating…" : "Update"}
        </Button>
      </div>
      <ul className="divide-y divide-border">
        {sorted.map((col, index) => (
          <li key={col.key} className="flex flex-wrap items-center gap-3 px-4 py-3 text-sm">
            <div className="flex flex-col gap-1">
              <button
                type="button"
                className="rounded border border-border px-1 text-xs"
                onClick={() => move(index, -1)}
                aria-label={`Move ${col.label} up`}
              >
                ↑
              </button>
              <button
                type="button"
                className="rounded border border-border px-1 text-xs"
                onClick={() => move(index, 1)}
                aria-label={`Move ${col.label} down`}
              >
                ↓
              </button>
            </div>
            <span className="w-28 font-mono text-xs text-fg-muted">{col.key}</span>
            <Input
              className="max-w-xs flex-1"
              value={col.label}
              onChange={(e) => patchRow(index, { label: e.target.value })}
              aria-label={`Label for ${col.key}`}
            />
            <label className="flex items-center gap-2">
              <Checkbox
                checked={col.active}
                onChange={(e) => patchRow(index, { active: e.target.checked })}
              />
              {col.active ? "Active" : "Inactive"}
            </label>
          </li>
        ))}
      </ul>
    </section>
  );
}
