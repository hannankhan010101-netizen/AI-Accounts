"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";

import { isPathAllowed } from "@/lib/rbac/route-modules";
import { useMyPermissions } from "@/lib/rbac/use-my-permissions";

/** Redirect to /forbidden when the current route's module is disabled. */
export function useModuleRouteGuard() {
  const pathname = usePathname();
  const router = useRouter();
  const { data, isLoading } = useMyPermissions();

  useEffect(() => {
    if (isLoading || pathname.startsWith("/forbidden")) return;
    const modules = data?.result?.modules ?? [];
    if (modules.length === 0) return;
    if (!isPathAllowed(pathname, modules)) {
      const params = new URLSearchParams({ from: pathname });
      router.replace(`/forbidden?${params.toString()}`);
    }
  }, [pathname, data?.result?.modules, isLoading, router]);
}
