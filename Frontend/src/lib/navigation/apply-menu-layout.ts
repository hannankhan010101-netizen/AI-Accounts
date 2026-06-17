import type { NavGroup } from "@/config/navigation";
import { navGroups } from "@/config/navigation";
import type { MenuItemSetting } from "@/lib/api/tenant";

/** Apply Content Settings menu layout to sidebar navigation. */
export function applyMenuLayout(groups: NavGroup[], items: MenuItemSetting[] | undefined): NavGroup[] {
  if (!items?.length) return groups;

  const byHref = new Map(items.map((i) => [i.href, i]));
  const out: NavGroup[] = [];

  for (const group of groups) {
    if (!group.items) {
      const cfg = group.href ? byHref.get(group.href) : undefined;
      if (cfg && !cfg.active) continue;
      out.push({
        ...group,
        label: cfg?.label?.trim() ? cfg.label : group.label,
      });
      continue;
    }

    const nextItems = group.items
      .map((item) => {
        const cfg = byHref.get(item.href);
        if (cfg && !cfg.active) return null;
        return {
          item,
          order: cfg?.order ?? 999,
          label: cfg?.label?.trim() ? cfg.label : item.label,
        };
      })
      .filter((row): row is NonNullable<typeof row> => row != null)
      .sort((a, b) => a.order - b.order)
      .map(({ item, label }) => ({ ...item, label }));

    if (nextItems.length === 0) continue;
    out.push({ ...group, items: nextItems });
  }

  return out.length ? out : groups;
}

export function defaultMenuItemsFromNav(): MenuItemSetting[] {
  const items: MenuItemSetting[] = [];
  let order = 0;
  for (const group of navGroups) {
    if (group.href) {
      items.push({
        href: group.href,
        group: group.label,
        label: group.label,
        active: true,
        order: order++,
      });
    }
    for (const item of group.items ?? []) {
      items.push({
        href: item.href,
        group: group.label,
        label: item.label,
        active: true,
        order: order++,
      });
    }
  }
  return items;
}
