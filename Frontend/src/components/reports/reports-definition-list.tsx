"use client";
import { useTenantReportQuery } from "@/lib/api/tenant-query";

import Link from "next/link";
import { useMemo, useState } from "react";


import { CollapsibleReportCategory } from "@/components/reports/collapsible-report-category";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { reportsApi } from "@/lib/api/tenant";
import { matchText } from "@/lib/list/document-list-filters";
import { reportIdHref, isGenericReportRunner } from "@/lib/reports/report-id-href";


export function ReportsDefinitionList() {
  const [search, setSearch] = useState("");
  const [hubFilter, setHubFilter] = useState<"all" | "standard" | "analytical">("all");
  const [expandAll, setExpandAll] = useState(true);

  const { data, isLoading, error } = useTenantReportQuery(["report-definitions", "catalog"], () => reportsApi.listDefinitions());

  const byCategory = useMemo(() => {
    const q = search.trim().toLowerCase();
    const grouped: Record<
      string,
      {
        reportId: string;
        name: string;
        hub: string;
        category: string;
        href: string;
        dedicated: boolean;
      }[]
    > = {};
    for (const row of data?.result ?? []) {
      if (hubFilter !== "all" && row.hub !== hubFilter) continue;
      if (q && !matchText([row.reportId, row.name, row.category, row.hub], q)) continue;
      if (!grouped[row.category]) grouped[row.category] = [];
      grouped[row.category].push({
        reportId: row.reportId,
        name: row.name,
        hub: row.hub,
        category: row.category,
        href: reportIdHref(row.reportId, { category: row.category }),
        dedicated: !isGenericReportRunner(row.reportId, { category: row.category }),
      });
    }
    return grouped;
  }, [data?.result, hubFilter, search]);

  const dedicatedCount = useMemo(() => {
    let count = 0;
    for (const row of data?.result ?? []) {
      if (!isGenericReportRunner(row.reportId, { category: row.category })) count += 1;
    }
    return count;
  }, [data?.result]);

  if (isLoading) {
    return <p className="text-sm text-fg-muted">Loading report catalog…</p>;
  }
  if (error instanceof Error) {
    return (
      <p className="text-sm text-status-danger" role="alert">
        {error.message}
      </p>
    );
  }

  const total = data?.result.length ?? 0;

  return (
    <>
      <p className="mb-3 text-sm text-fg-muted">
        {total} FastAccounts report definitions — {dedicatedCount} with dedicated pages,{" "}
        {total - dedicatedCount} via generic runner.
      </p>
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <div className="max-w-md flex-1">
          <Input
            type="search"
            placeholder="Search by ID, name, or category…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Search full report catalog"
          />
        </div>
        <Button type="button" variant="outline" size="sm" onClick={() => setExpandAll((v) => !v)}>
          {expandAll ? "Collapse all" : "Expand all"}
        </Button>
        <div className="flex gap-2 text-sm">
          {(["all", "standard", "analytical"] as const).map((h) => (
            <button
              key={h}
              type="button"
              onClick={() => setHubFilter(h)}
              className={`rounded-md border px-3 py-1.5 capitalize ${
                hubFilter === h
                  ? "border-brand bg-brand/10 text-brand"
                  : "border-border bg-surface text-fg hover:bg-canvas"
              }`}
            >
              {h}
            </button>
          ))}
        </div>
      </div>
      <div className="space-y-4">
        {Object.entries(byCategory).map(([category, items]) => (
          <CollapsibleReportCategory
            key={`${category}-${expandAll ? "open" : "closed"}`}
            title={category}
            count={items.length}
            defaultOpen={expandAll}
          >
            <ul>
              {items.map((it) => (
                <li key={it.reportId} className="border-b border-border last:border-b-0">
                  <Link
                    href={it.href}
                    className="flex items-center gap-3 px-4 py-2 text-sm hover:bg-canvas"
                  >
                    <span className="inline-block w-16 shrink-0 font-mono text-xs text-fg-muted">
                      {it.reportId}
                    </span>
                    <span className="font-medium text-fg">{it.name}</span>
                    <span
                      className={`ml-auto rounded px-2 py-0.5 text-xs ${
                        it.dedicated
                          ? "bg-status-success/10 text-status-success"
                          : "bg-canvas text-fg-muted"
                      }`}
                    >
                      {it.dedicated ? "Dedicated" : "Runner"}
                    </span>
                    <span className="text-xs capitalize text-fg-muted">{it.hub}</span>
                  </Link>
                </li>
              ))}
            </ul>
          </CollapsibleReportCategory>
        ))}
        {Object.keys(byCategory).length === 0 && (
          <p className="text-sm text-fg-muted">No reports match your search.</p>
        )}
      </div>
    </>
  );
}
