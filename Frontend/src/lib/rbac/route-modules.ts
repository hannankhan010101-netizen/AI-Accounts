/** Map URL prefixes to RBAC module codes for route guards. */

const PATH_PREFIX_MODULES: readonly [string, string][] = [
  ["/sales", "sales"],
  ["/purchases", "purchases"],
  ["/bank", "bank"],
  ["/inventory", "inventory"],
  ["/reports", "financial"],
  ["/settings/journals", "financial"],
  ["/settings/coa", "financial"],
  ["/settings/taxes-year-end", "financial"],
  ["/settings/lock-date", "financial"],
  ["/settings/authorisation", "financial"],
];

export function moduleForPath(pathname: string): string | null {
  for (const [prefix, code] of PATH_PREFIX_MODULES) {
    if (pathname === prefix || pathname.startsWith(`${prefix}/`)) {
      return code;
    }
  }
  return null;
}

export function isPathAllowed(
  pathname: string,
  modules: {
    moduleCode: string;
    canAccess?: boolean;
    routesEnabled?: boolean;
    reportsEnabled?: boolean;
  }[],
): boolean {
  const code = moduleForPath(pathname);
  if (!code) return true;
  const row = modules.find((m) => m.moduleCode === code);
  if (!row) return true;
  if (!row.canAccess || !(row.routesEnabled ?? true)) return false;
  if (pathname.startsWith("/reports") && !(row.reportsEnabled ?? true)) return false;
  return true;
}
