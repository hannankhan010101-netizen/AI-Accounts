"use client";

import type { ReactNode } from "react";

import { useMyPermissions } from "@/lib/rbac/use-my-permissions";
import { hasPermission } from "@/lib/rbac/permissions";

type CanProps = {
  permission: string;
  children: ReactNode;
  fallback?: ReactNode;
};

export function Can({ permission, children, fallback = null }: CanProps) {
  const { can } = useMyPermissions();
  if (!can(permission)) return <>{fallback}</>;
  return <>{children}</>;
}

export function usePermission(code: string): boolean {
  const { can } = useMyPermissions();
  return can(code);
}

export function useModuleAccess(moduleCode: string): boolean {
  const { data } = useMyPermissions();
  const modules = data?.result?.modules ?? [];
  const row = modules.find((m) => m.moduleCode === moduleCode);
  return row?.canAccess ?? true;
}

export function filterByPermission<T extends { requiredPermission?: string }>(
  items: T[],
  permissions: string[],
): T[] {
  return items.filter((item) => {
    if (!item.requiredPermission) return true;
    return hasPermission(permissions, item.requiredPermission);
  });
}
