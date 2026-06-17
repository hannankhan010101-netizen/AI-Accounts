"use client";
import { useTenantReportQuery } from "@/lib/api/tenant-query";

import Link from "next/link";
import { useMemo } from "react";


import { CollapsibleReportCategory } from "@/components/reports/collapsible-report-category";
import { reportsApi } from "@/lib/api/tenant";
import { matchText } from "@/lib/list/document-list-filters";
import { isGenericReportRunner, reportIdHref } from "@/lib/reports/report-id-href";


/** FastAccounts module tree — groups catalog definitions by FA category. */
export function ReportsModuleTree({
  search = "",
  expandAll = true,
}: {
  search?: string;
  expandAll?: boolean;
}) {
  const { data, isLoading, error } = useTenantReportQuery(["report-definitions", "modules"], () => reportsApi.listDefinitions({ hub: "standard" }));

  const byCategory = useMemo(() => {
    const q = search.trim().toLowerCase();
    const grouped: Record<
      string,
      { reportId: string; name: string; href: string; dedicated: boolean }[]
    > = {};
    for (const row of data?.result ?? []) {
      if (q && !matchText([row.reportId, row.name, row.category], q)) continue;
      if (!grouped[row.category]) grouped[row.category] = [];
      grouped[row.category].push({
        reportId: row.reportId,
        name: row.name,
        href: reportIdHref(row.reportId, { category: row.category }),
        dedicated: !isGenericReportRunner(row.reportId, { category: row.category }),
      });
    }
    for (const items of Object.values(grouped)) {
      items.sort((a, b) => a.name.localeCompare(b.name));
    }
    return grouped;
  }, [data?.result, search]);

  const moduleOrder = useMemo(() => {
    const preferred = [
      "Financial",
      "Budget",
      "Bank",
      "Sales and Customer",
      "Purchases and Suppliers",
      "Inventory Products",
      "Assembly",
      "Projects",
      "Favorites",
    ];
    const keys = Object.keys(byCategory);
    return [
      ...preferred.filter((k) => keys.includes(k)),
      ...keys.filter((k) => !preferred.includes(k)).sort(),
    ];
  }, [byCategory]);

  if (isLoading) {
    return <p className="text-sm text-fg-muted">Loading FA report modules…</p>;
  }
  if (error instanceof Error) {
    return (
      <p className="text-sm text-status-danger" role="alert">
        {error.message}
      </p>
    );
  }

  const total = data?.result.length ?? 0;
  const dedicatedCount = (data?.result ?? []).filter(
    (row) => !isGenericReportRunner(row.reportId, { category: row.category }),
  ).length;

  return (
    <>
      <p className="mb-3 text-sm text-fg-muted">
        {moduleOrder.length} FA modules · {total} standard reports · {dedicatedCount} dedicated
        pages
      </p>
      <div className="space-y-4">
        {moduleOrder.map((category) => {
          const items = byCategory[category] ?? [];
          if (!items.length) return null;
          return (
            <CollapsibleReportCategory
              key={`${category}-${expandAll ? "open" : "closed"}`}
              title={category}
              count={items.length}
              defaultOpen={expandAll}
            >
              <ul>
                {items.map((it) => (
                  <li key={`${category}-${it.reportId}`} className="border-b border-border last:border-b-0">
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
                    </Link>
                  </li>
                ))}
              </ul>
            </CollapsibleReportCategory>
          );
        })}
        {moduleOrder.length === 0 && (
          <p className="text-sm text-fg-muted">No modules match your search.</p>
        )}
      </div>
    </>
  );
}
