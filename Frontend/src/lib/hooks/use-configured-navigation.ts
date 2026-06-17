"use client";

import { useMemo } from "react";

import { navGroups, type NavGroup } from "@/config/navigation";
import { rbacApi } from "@/lib/api/tenant";
import { useTenantReferenceQuery } from "@/lib/api/tenant-query";
import { applyMenuLayout } from "@/lib/navigation/apply-menu-layout";
import { appSettingsApi } from "@/lib/api/tenant";

function filterNavByModules(groups: NavGroup[], modules: { moduleCode: string; canAccess: boolean; sidebarVisible?: boolean; reportsEnabled?: boolean }[]): NavGroup[] {
  const access = new Map(
    modules.map((m) => [
      m.moduleCode,
      m.canAccess && (m.sidebarVisible ?? true),
    ]),
  );
  const reportsEnabled = new Map(
    modules.map((m) => [m.moduleCode, m.reportsEnabled ?? true]),
  );
  return groups
    .filter((group) => {
      if (!group.moduleCode) return true;
      return access.get(group.moduleCode) ?? true;
    })
    .map((group) => {
      if (!group.items?.length) return group;
      const items = group.items.filter((item) => {
        if (!item.href.startsWith("/reports")) return true;
        const code = group.moduleCode ?? "financial";
        return reportsEnabled.get(code) ?? true;
      });
      return { ...group, items };
    });
}

/** Sidebar navigation with Content Settings menu overrides and RBAC module filtering. */
export function useConfiguredNavGroups() {
  const { data: menuData } = useTenantReferenceQuery(["content-menu"], () =>
    appSettingsApi.getMenuLayout(),
  );
  const { data: permsData } = useTenantReferenceQuery(["my-permissions"], () =>
    rbacApi.getMyPermissions(),
  );

  return useMemo(() => {
    const laidOut = applyMenuLayout(navGroups, menuData?.result.items);
    const modules = permsData?.result?.modules ?? [];
    if (modules.length === 0) return laidOut;
    return filterNavByModules(laidOut, modules);
  }, [menuData?.result.items, permsData?.result?.modules]);
}
