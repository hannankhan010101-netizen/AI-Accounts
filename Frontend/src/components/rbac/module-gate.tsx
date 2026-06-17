"use client";

import type { ReactNode } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { isPathAllowed, moduleForPath } from "@/lib/rbac/route-modules";
import { useMyPermissions } from "@/lib/rbac/use-my-permissions";

type ModuleGateProps = {
  children: ReactNode;
};

/** Block page content when the route module is disabled (fallback if guard missed). */
export function ModuleGate({ children }: ModuleGateProps) {
  const pathname = usePathname();
  const { data, isLoading } = useMyPermissions();
  const modules = data?.result?.modules ?? [];

  if (isLoading || modules.length === 0) {
    return <>{children}</>;
  }

  if (isPathAllowed(pathname, modules)) {
    return <>{children}</>;
  }

  const code = moduleForPath(pathname);
  return (
    <div className="rounded-lg border border-border/60 bg-surface-elevated p-6">
      <h2 className="text-lg font-semibold text-fg">Module unavailable</h2>
      <p className="mt-2 text-sm text-fg-muted">
        {code
          ? `The ${code} module is disabled for your company or you lack access.`
          : "This area is not available for your account."}
      </p>
      <Button asChild className="mt-4" variant="outline">
        <Link href="/dashboard">Return to dashboard</Link>
      </Button>
    </div>
  );
}
