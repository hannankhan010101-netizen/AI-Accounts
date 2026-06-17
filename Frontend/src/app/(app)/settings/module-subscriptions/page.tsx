/** Company module entitlements — P11. */
"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { invalidateTenantQueries, useTenantReferenceQuery } from "@/lib/api/tenant-query";

import { BillingReadinessBanner } from "@/components/settings/billing-readiness-banner";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { WorkspaceLoading } from "@/components/ui/workspace-loading";
import { billingApi, modulesApi } from "@/lib/api/tenant";
export default function ModuleSubscriptionsPage() {
  const qc = useQueryClient();
  const { data, isLoading } = useTenantReferenceQuery(["module-entitlements"], () => modulesApi.listEntitlements());

  const portal = useMutation({
    mutationFn: () => billingApi.portalSession(),
    onSuccess: (data) => {
      const url = data?.result?.url;
      if (url && typeof window !== "undefined") {
        window.location.href = url;
      }
    },
    onSettled: () => void invalidateTenantQueries(qc, "billing-status"),
  });

  const checkout = useMutation({
    mutationFn: (planCode: "starter" | "pro") =>
      billingApi.checkoutSession({ planCode }),
    onSuccess: (data) => {
      const url = data?.result?.url;
      if (url && typeof window !== "undefined") {
        window.location.href = url;
      }
    },
    onSettled: () => void invalidateTenantQueries(qc, "billing-status"),
  });

  const save = useMutation({
    mutationFn: (entitlements: { moduleCode: string; enabled: boolean }[]) =>
      modulesApi.replaceEntitlements(entitlements),
    onSuccess: () => void invalidateTenantQueries(qc, "module-entitlements"),
  });

  const rows = data?.result ?? [];

  return (
    <div>
      <PageHeader
        title="Module subscriptions"
        breadcrumb="Settings / Module subscriptions"
        description="Disable modules to block gated APIs (assembly, FBR, online payments, etc.)."
      />
      <BillingReadinessBanner />
      {isLoading ? (
        <WorkspaceLoading />
      ) : (
        <ul className="max-w-md space-y-2 rounded-lg border border-border bg-surface p-4">
          {rows.map((row) => (
            <li key={row.moduleCode} className="flex items-center justify-between text-sm">
              <span className="font-medium capitalize text-fg">{row.moduleCode}</span>
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={row.enabled}
                  onChange={(e) => {
                    const next = rows.map((r) =>
                      r.moduleCode === row.moduleCode
                        ? { ...r, enabled: e.target.checked }
                        : r
                    );
                    save.mutate(next);
                  }}
                />
                <span className="text-fg-muted">Enabled</span>
              </label>
            </li>
          ))}
        </ul>
      )}
      {save.isError ? (
        <p className="mt-2 text-sm text-status-danger">
          {save.error instanceof Error ? save.error.message : "Save failed"}
        </p>
      ) : null}
      <div className="mt-6 flex flex-wrap gap-2">
        <Button
          type="button"
          disabled={checkout.isPending}
          onClick={() => checkout.mutate("starter")}
        >
          Subscribe — Starter
        </Button>
        <Button
          type="button"
          variant="outline"
          disabled={checkout.isPending}
          onClick={() => checkout.mutate("pro")}
        >
          Subscribe — Pro
        </Button>
        <Button
          type="button"
          variant="outline"
          disabled={portal.isPending}
          onClick={() => portal.mutate()}
        >
          Manage billing
        </Button>
      </div>
      {portal.isError ? (
        <p className="mt-2 text-sm text-status-danger">
          {portal.error instanceof Error ? portal.error.message : "Portal failed"}
        </p>
      ) : null}
      {checkout.isError ? (
        <p className="mt-2 text-sm text-status-danger">
          {checkout.error instanceof Error ? checkout.error.message : "Checkout failed"}
        </p>
      ) : null}
      <Button type="button" className="mt-4" variant="outline" disabled={save.isPending}>
        Changes save on toggle
      </Button>
    </div>
  );
}
