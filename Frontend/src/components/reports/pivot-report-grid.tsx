"use client";

import { useMemo, useState } from "react";

import { Input } from "@/components/ui/input";
import { ScrollHint } from "@/components/ui/scroll-hint";
import { cn } from "@/lib/utils";

export interface PivotReportRow {
  categoryType: string;
  categoryName: string;
  amounts: Record<string, string>;
}

interface PivotReportGridProps {
  periods: string[];
  rows: PivotReportRow[];
  loading?: boolean;
  emptyMessage?: string;
}

export function PivotReportGrid({
  periods,
  rows,
  loading,
  emptyMessage = "No data for this report.",
}: PivotReportGridProps) {
  const [search, setSearch] = useState("");

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return rows;
    return rows.filter((r) =>
      [r.categoryType, r.categoryName, ...periods.map((p) => r.amounts[p])]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(q),
    );
  }, [rows, periods, search]);

  if (loading) {
    return <p className="text-sm text-fg-muted">Loading…</p>;
  }

  if (rows.length === 0 || periods.length === 0) {
    return <p className="text-sm text-fg-muted">{emptyMessage}</p>;
  }

  return (
    <div className="space-y-3">
      <div className="max-w-md">
        <Input
          type="search"
          placeholder="Search categories…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          aria-label="Search pivot report"
        />
      </div>
      <div className="relative overflow-x-auto rounded-lg border border-border bg-surface scrollbar-gutter-stable max-h-[min(70vh,640px)] max-h-sm:max-h-[min(50vh,400px)] overflow-y-auto">
        <ScrollHint />
        <table className="min-w-full text-sm">
          <thead>
            <tr className="border-b border-border bg-canvas text-left text-xs uppercase text-fg-muted">
              <th className="sticky left-0 z-10 min-w-[7rem] bg-canvas px-4 py-2">Type</th>
              <th className="sticky left-[7rem] z-10 min-w-[10rem] bg-canvas px-4 py-2">
                Category
              </th>
              {periods.map((p) => (
                <th key={p} className="whitespace-nowrap px-4 py-2 text-right">
                  {p}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((r) => (
              <tr
                key={`${r.categoryType}-${r.categoryName}`}
                className="border-b border-border hover:bg-canvas/80"
              >
                <td className="sticky left-0 z-[1] bg-surface px-4 py-2">{r.categoryType}</td>
                <td className="sticky left-[7rem] z-[1] bg-surface px-4 py-2 font-medium">
                  {r.categoryName}
                </td>
                {periods.map((p) => (
                  <td key={p} className="px-4 py-2 text-right tabular-nums">
                    {r.amounts[p] ?? "—"}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <p className="p-4 text-center text-sm text-fg-muted">No rows match your search.</p>
        )}
      </div>
      <p className={cn("text-xs text-fg-muted")}>
        {filtered.length} of {rows.length} categories · scroll horizontally for more periods
      </p>
    </div>
  );
}
