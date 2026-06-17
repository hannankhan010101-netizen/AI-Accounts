/** True when pathname is exactly href or a nested route under href. */
export function isNavActive(pathname: string, href: string): boolean {
  if (href === "/dashboard") return pathname === "/dashboard";
  return pathname === href || pathname.startsWith(`${href}/`);
}

/** Nav group label to expand when any child (or group href) matches pathname. */
export function expandedGroupsForPath(
  pathname: string,
  groups: { label: string; href?: string; items?: { href: string }[] }[],
): Record<string, boolean> {
  const out: Record<string, boolean> = {};
  for (const g of groups) {
    if (g.href && isNavActive(pathname, g.href)) {
      out[g.label] = true;
      continue;
    }
    if (g.items?.some((item) => isNavActive(pathname, item.href))) {
      out[g.label] = true;
    }
  }
  return out;
}
