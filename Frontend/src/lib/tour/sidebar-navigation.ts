import { navGroups } from "@/config/navigation";

/** `data-tour` id for a sidebar nav link from its href. */
export function tourNavTargetId(href: string): string {
  return `nav-${href.replace(/^\//, "").replace(/\//g, "-")}`;
}

/** Inverse of `tourNavTargetId` — e.g. `nav-sales-invoices` → `/sales/invoices`. */
export function hrefFromNavTourTargetId(targetId: string): string | null {
  if (!targetId.startsWith("nav-")) return null;
  const tail = targetId.slice(4);
  if (!tail) return null;
  return `/${tail.replace(/-/g, "/")}`;
}

export function isNavTourTargetId(targetId: string): boolean {
  return targetId === "sidebar-nav" || targetId.startsWith("nav-");
}

/** Nav group label that contains this href (e.g. Sell → /sales/invoices). */
export function navGroupForHref(href: string): string | null {
  for (const group of navGroups) {
    if (group.href === href) return group.label;
    if (group.items?.some((item) => item.href === href || href.startsWith(`${item.href}/`))) {
      return group.label;
    }
  }
  return null;
}

export function pathnameMatchesRoute(pathname: string, route: string): boolean {
  if (pathname === route) return true;
  return pathname.startsWith(`${route}/`);
}
