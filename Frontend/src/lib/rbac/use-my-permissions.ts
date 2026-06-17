"use client";
import { useTenantReferenceQuery } from "@/lib/api/tenant-query";

import { rbacApi } from "@/lib/api/tenant";
import { hasPermission } from "@/lib/rbac/permissions";

export function useMyPermissions() {
  const query = useTenantReferenceQuery(["my-permissions"], () => rbacApi.getMyPermissions());

  const permissions = query.data?.result.permissions ?? [];

  return {
    ...query,
    permissions,
    can: (code: string) => hasPermission(permissions, code),
  };
}
