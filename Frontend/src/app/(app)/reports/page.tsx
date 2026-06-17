/** Reports hub — catalog §10.10 */
"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Star } from "lucide-react";

import { CollapsibleReportCategory } from "@/components/reports/collapsible-report-category";
import { ReportsModuleTree } from "@/components/reports/reports-module-tree";
import { ReportsDefinitionList } from "@/components/reports/reports-definition-list";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { Input } from "@/components/ui/input";
import { reportCatalog, reportCatalogByCategory, type ReportCatalogItem } from "@/config/reports-catalog";
import { useCompany } from "@/lib/auth/company-context";
import {
  fetchReportFavorites,
  persistReportFavorites,
  toggleReportFavorite,
} from "@/lib/reports/favorites";
import { matchText } from "@/lib/list/document-list-filters";
import { cn } from "@/lib/utils";

export default function ReportsHubPage() {
  const { companyId } = useCompany();
  const [favorites, setFavorites] = useState<Set<string>>(() => new Set());
  const [search, setSearch] = useState("");
  const [expandAll, setExpandAll] = useState(true);
  const [hubMode, setHubMode] = useState<"shortcuts" | "modules" | "all">("shortcuts");

  useEffect(() => {
    let cancelled = false;
    void fetchReportFavorites(companyId).then((set) => {
      if (!cancelled) setFavorites(set);
    });
    return () => {
      cancelled = true;
    };
  }, [companyId]);

  const favoriteItems = useMemo(
    () => reportCatalog.filter((r) => favorites.has(r.href)),
    [favorites],
  );

  const filteredByCategory = useMemo(() => {
    const q = search.trim().toLowerCase();
    const out: Record<string, ReportCatalogItem[]> = {};
    for (const [category, items] of Object.entries(reportCatalogByCategory)) {
      const filtered = q
        ? items.filter((it) => matchText([it.id, it.name, category], q))
        : items;
      if (filtered.length) out[category] = filtered;
    }
    return out;
  }, [search]);

  function onToggleFavorite(e: React.MouseEvent, href: string) {
    e.preventDefault();
    e.stopPropagation();
    const next = toggleReportFavorite(companyId, href, favorites);
    setFavorites(next);
    void persistReportFavorites(companyId, next).then(setFavorites);
  }

  return (
    <div>
      <PageHeader
        title="Insights"
        breadcrumb="Insights / Reports"
        description="Star favorites for quick access. Use Ctrl+K to jump to any report."
        tourRoot="reports-hub-header"
        actions={
          <div className="flex flex-wrap gap-2">
            <Link
              href="/reports/catalog"
              className="inline-flex h-9 items-center rounded-md border border-border bg-surface px-3 text-sm font-medium text-fg hover:bg-canvas"
            >
              Full catalog
            </Link>
            <Link
              href="/reports/analytical"
              className="inline-flex h-9 items-center rounded-md border border-border bg-surface px-3 text-sm font-medium text-fg hover:bg-canvas"
            >
              Analytical reports
            </Link>
          </div>
        }
      />

      <div className="mb-4 flex flex-wrap items-center gap-3">
        <div className="flex rounded-md border border-border p-0.5">
          <button
            type="button"
            onClick={() => setHubMode("shortcuts")}
            className={cn(
              "rounded px-3 py-1.5 text-xs font-medium",
              hubMode === "shortcuts"
                ? "bg-brand/10 text-brand"
                : "text-fg-muted hover:bg-canvas",
            )}
          >
            Shortcuts
          </button>
          <button
            type="button"
            onClick={() => setHubMode("modules")}
            className={cn(
              "rounded px-3 py-1.5 text-xs font-medium",
              hubMode === "modules"
                ? "bg-brand/10 text-brand"
                : "text-fg-muted hover:bg-canvas",
            )}
          >
            FA modules
          </button>
          <button
            type="button"
            onClick={() => setHubMode("all")}
            className={cn(
              "rounded px-3 py-1.5 text-xs font-medium",
              hubMode === "all" ? "bg-brand/10 text-brand" : "text-fg-muted hover:bg-canvas",
            )}
          >
            All reports
          </button>
        </div>
        {hubMode === "shortcuts" || hubMode === "modules" ? (
          <>
            <div className="max-w-md flex-1">
              <Input
                type="search"
                placeholder={hubMode === "modules" ? "Search modules…" : "Search reports…"}
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                aria-label="Search reports"
                data-tour="reports-hub-search"
              />
            </div>
            {hubMode === "shortcuts" || hubMode === "modules" ? (
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => setExpandAll((v) => !v)}
              >
                {expandAll ? "Collapse all" : "Expand all"}
              </Button>
            ) : null}
          </>
        ) : null}
      </div>

      {hubMode === "all" ? <ReportsDefinitionList /> : null}

      {hubMode === "modules" ? (
        <ReportsModuleTree search={search} expandAll={expandAll} />
      ) : null}

      {hubMode === "shortcuts" ? (
      <section
        className="mb-6 overflow-hidden rounded-lg border border-border bg-surface"
        data-tour="reports-hub-favorites"
      >
        <div className="border-b border-border px-4 py-2 text-sm font-semibold text-fg">
          Favorites
        </div>
        {favoriteItems.length > 0 ? (
          <ul>
            {favoriteItems.map((it) => (
              <ReportRow key={it.href} item={it} starred onToggle={onToggleFavorite} />
            ))}
          </ul>
        ) : (
          <p className="px-4 py-3 text-sm text-fg-muted">
            Star any report below to pin it here for quick access.
          </p>
        )}
      </section>
      ) : null}

      {hubMode === "shortcuts" ? (
      <div className="space-y-4">
        {Object.entries(filteredByCategory).map(([category, items]) => (
          <CollapsibleReportCategory
            key={`${category}-${expandAll ? "open" : "closed"}`}
            title={category}
            count={items.length}
            defaultOpen={expandAll}
          >
            <ul>
              {items.map((it) => (
                <ReportRow
                  key={it.href}
                  item={it}
                  starred={favorites.has(it.href)}
                  onToggle={onToggleFavorite}
                />
              ))}
            </ul>
          </CollapsibleReportCategory>
        ))}
        {Object.keys(filteredByCategory).length === 0 && (
          <p className="text-sm text-fg-muted">No reports match your search.</p>
        )}
      </div>
      ) : null}
    </div>
  );
}

function ReportRow({
  item,
  starred,
  onToggle,
}: {
  item: ReportCatalogItem;
  starred: boolean;
  onToggle: (e: React.MouseEvent, href: string) => void;
}) {
  return (
    <li className="border-b border-border last:border-b-0">
      <div className="flex items-center gap-1 px-2 py-1">
        <button
          type="button"
          onClick={(e) => onToggle(e, item.href)}
          className="rounded p-1.5 text-fg-muted hover:bg-canvas"
          aria-label={starred ? "Remove from favorites" : "Add to favorites"}
        >
          <Star
            className={cn("h-4 w-4", starred && "fill-status-warning text-status-warning")}
            aria-hidden
          />
        </button>
        <Link
          href={item.href}
          className="flex flex-1 items-center gap-3 py-1.5 text-sm hover:bg-canvas"
        >
          <span className="inline-block w-14 shrink-0 font-mono text-xs text-fg-muted">
            {item.id}
          </span>
          <span className="font-medium text-fg">{item.name}</span>
        </Link>
      </div>
    </li>
  );
}
