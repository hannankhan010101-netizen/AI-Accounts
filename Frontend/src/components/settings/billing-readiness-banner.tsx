"use client";
import { useTenantReferenceQuery } from "@/lib/api/tenant-query";



import { billingApi, type BillingProviderStatus } from "@/lib/api/tenant";


function modeLabel(mode?: BillingProviderStatus["mode"], ready?: boolean) {
  if (ready) return "Live";
  if (mode === "stub") return "Stub (dev)";
  return "Not configured";
}

export function BillingReadinessBanner() {
  const { data, isLoading } = useTenantReferenceQuery(["billing-status"], () => billingApi.status());

  if (isLoading) return null;
  const result = data?.result;
  if (!result) return null;

  const billing = result.billing;
  const seats = result.seats;
  const ready = billing?.ready;

  return (
    <div className="mb-6 space-y-4">
      <div className="rounded-lg border border-border bg-surface p-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h3 className="font-medium text-fg">Stripe billing</h3>
          <span
            className={
              ready
                ? "rounded-full bg-status-success/15 px-2 py-0.5 text-xs text-status-success"
                : "rounded-full bg-status-warning/15 px-2 py-0.5 text-xs text-status-warning"
            }
          >
            {modeLabel(billing?.mode, ready)}
          </span>
        </div>
        <p className="mt-2 text-xs text-fg-muted">
          {ready
            ? "Checkout and customer portal use live Stripe credentials."
            : "Dev stub mode: checkout redirects without charging. Set env vars for live billing."}
        </p>
        {!ready && (billing?.missingEnvKeys?.length ?? 0) > 0 ? (
          <ul className="mt-2 space-y-1 font-mono text-xs text-fg-muted">
            {billing?.missingEnvKeys?.map((key) => (
              <li key={key}>{key}</li>
            ))}
          </ul>
        ) : null}
      </div>

      {seats ? (
        <div className="rounded-lg border border-border bg-canvas px-4 py-3 text-sm">
          <span className="font-medium text-fg">Seats: </span>
          <span className="text-fg-muted">
            {seats.used}
            {seats.limit != null ? ` / ${seats.limit}` : " (unlimited)"} used
          </span>
          {seats.atLimit ? (
            <p className="mt-1 text-xs text-status-danger">
              Seat limit reached for plan {result.planCode}. Revoke a member or upgrade before inviting.
            </p>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
