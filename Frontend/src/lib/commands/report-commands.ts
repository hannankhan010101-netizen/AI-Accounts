import { commandItems, filterCommands, type CommandItem } from "@/config/command-registry";
import { reportCatalog } from "@/config/reports-catalog";

/** Map Insights catalog entries to command-palette items. */
export function reportCatalogCommands(): CommandItem[] {
  return reportCatalog.map((r) => ({
    id: `report-${r.id}`,
    label: r.name,
    description: r.category,
    href: r.href,
    kind: "navigate" as const,
    keywords: ["report", "insights", r.id, r.category.toLowerCase()],
  }));
}

export function favoriteReportCommands(favoriteHrefs: Set<string>): CommandItem[] {
  return reportCatalogCommands().filter((c) => favoriteHrefs.has(c.href));
}

export function buildCommandList(favoriteHrefs: Set<string>): CommandItem[] {
  const catalog = reportCatalogCommands();
  const favs = favoriteReportCommands(favoriteHrefs);
  if (favs.length === 0) return [...commandItems, ...catalog];
  const favIds = new Set(favs.map((c) => c.id));
  const rest = [...commandItems, ...catalog].filter((c) => !favIds.has(c.id));
  const starred = favs.map((c) => ({
    ...c,
    label: `★ ${c.label}`,
    keywords: [...(c.keywords ?? []), "favorite", "starred"],
  }));
  return [...starred, ...rest];
}

export function filterAllCommands(query: string, favoriteHrefs: Set<string>): CommandItem[] {
  return filterCommands(query, buildCommandList(favoriteHrefs));
}
