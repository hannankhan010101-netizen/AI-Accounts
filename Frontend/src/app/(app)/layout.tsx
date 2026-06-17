"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { MobileBottomNav } from "@/components/app/mobile-bottom-nav";
import { OfflineBanner } from "@/components/app/offline-banner";
import { Sidebar } from "@/components/app/sidebar";
import { TopBar } from "@/components/app/top-bar";
import { DashboardSkeleton } from "@/components/dashboard/dashboard-skeleton";
import { Button } from "@/components/ui/button";
import { MotionFade } from "@/components/ui/motion-fade";
import { CompanyProvider, useCompany } from "@/lib/auth/company-context";
import { clearTokens, getTokens } from "@/lib/auth/storage";
import { TourRoot } from "@/components/tour/tour-root";
import { AssistantProvider } from "@/features/assistant/providers/assistant-provider";
import { CopilotRoot } from "@/features/assistant/copilot-root";
import { useCopilotShortcut } from "@/features/assistant/hooks/use-copilot-shortcut";
import { ShellProvider } from "@/lib/layout/shell-context";
import { ModuleGate } from "@/components/rbac/module-gate";
import { useModuleRouteGuard } from "@/lib/rbac/use-module-route-guard";

function AppShell({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isLoading, companyId, bootstrapError, retryBootstrap } = useCompany();
  useCopilotShortcut();
  useModuleRouteGuard();

  if (isLoading) {
    return (
      <div className="flex min-h-dvh items-center justify-center bg-canvas p-6">
        <DashboardSkeleton className="w-full max-w-4xl" />
      </div>
    );
  }

  if (bootstrapError) {
    return (
      <div className="flex min-h-dvh items-center justify-center bg-canvas p-6">
        <div className="w-full max-w-md rounded-xl border border-status-danger/30 bg-surface-elevated p-6 shadow-md">
          <h1 className="text-lg font-semibold text-fg">Could not load workspace</h1>
          <p className="mt-2 text-sm text-fg-muted">{bootstrapError}</p>
          <div className="mt-4 flex flex-wrap gap-2">
            <Button type="button" onClick={retryBootstrap}>
              Retry
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                clearTokens();
                router.replace("/login");
              }}
            >
              Sign out
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-dvh max-h-dvh min-h-0 flex-col overflow-hidden md:flex-row">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-[max(1rem,env(safe-area-inset-top))] focus:z-50 focus:rounded-md focus:bg-surface focus:px-3 focus:py-2 focus:text-sm focus:shadow-md"
      >
        Skip to main content
      </a>
      <Sidebar />
      <div className="flex min-h-0 min-w-0 flex-1 flex-col overflow-hidden">
        <TopBar />
        <OfflineBanner />
        <main
          id="main-content"
          data-tour="main-content"
          className="min-h-0 flex-1 overflow-y-auto overscroll-y-contain px-safe pt-3 pb-[calc(var(--bottom-nav-height)+env(safe-area-inset-bottom,0px)+1rem)] md:px-6 md:pt-4 md:pb-6"
        >
          {!companyId ? (
            <div className="rounded-md border border-status-warning/30 bg-status-warning/10 p-4 text-sm text-status-warning">
              No company is linked to your account. Open{" "}
              <a href="/admin" className="font-medium underline">
                Admin
              </a>{" "}
              or contact an administrator.
            </div>
          ) : (
            <MotionFade>
              <ModuleGate>{children}</ModuleGate>
            </MotionFade>
          )}
        </main>
        <MobileBottomNav />
      </div>
    </div>
  );
}

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!getTokens()) {
      router.replace("/login");
      return;
    }
    setReady(true);
  }, [router]);

  if (!ready) {
    return (
      <div className="flex min-h-dvh items-center justify-center bg-canvas p-6">
        <DashboardSkeleton className="w-full max-w-md" />
      </div>
    );
  }

  return (
    <CompanyProvider>
      <AssistantProvider>
        <TourRoot>
          <ShellProvider>
            <AppShell>{children}</AppShell>
            <CopilotRoot />
          </ShellProvider>
        </TourRoot>
      </AssistantProvider>
    </CompanyProvider>
  );
}
