"use client";
import { useTenantReferenceQuery } from "@/lib/api/tenant-query";

import Link from "next/link";


import { integrationsApi, type IntegrationProviderStatus } from "@/lib/api/tenant";


function modeLabel(mode?: IntegrationProviderStatus["mode"], ready?: boolean) {
  if (ready) return "Live";
  if (mode === "stub") return "Stub (dev)";
  if (mode === "off") return "Off";
  return "Not configured";
}

function ProviderCard({
  title,
  provider,
  docsHref,
}: {
  title: string;
  provider: IntegrationProviderStatus;
  docsHref?: string;
}) {
  const ready = provider.ready;
  return (
    <div className="rounded-lg border border-border bg-surface p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="font-medium text-fg">{title}</h3>
        <span
          className={
            ready
              ? "rounded-full bg-status-success/15 px-2 py-0.5 text-xs text-status-success"
              : provider.mode === "stub"
                ? "rounded-full bg-status-warning/15 px-2 py-0.5 text-xs text-status-warning"
                : "rounded-full bg-canvas px-2 py-0.5 text-xs text-fg-muted"
          }
        >
          {modeLabel(provider.mode, ready)}
        </span>
      </div>
      <p className="mt-2 text-xs text-fg-muted">
        {ready
          ? "Production credentials detected on the API server."
          : provider.stubAvailable
            ? "Stub/dev flow available. Set env vars below for live mode."
            : "Enable the provider flag and set required env vars."}
      </p>
      {!ready && (provider.missingEnvKeys?.length ?? 0) > 0 ? (
        <ul className="mt-2 space-y-1 font-mono text-xs text-fg-muted">
          {provider.missingEnvKeys?.map((key) => (
            <li key={key}>{key}</li>
          ))}
        </ul>
      ) : null}
      {docsHref ? (
        <Link href={docsHref} className="mt-3 inline-block text-xs font-medium text-brand hover:underline">
          Open related settings →
        </Link>
      ) : null}
    </div>
  );
}

export function IntegrationReadinessBanner({ compact = false }: { compact?: boolean }) {
  const { data, isLoading } = useTenantReferenceQuery(["integrations-readiness"], () => integrationsApi.getReadiness());

  if (isLoading) return null;
  const r = data?.result;
  if (!r) return null;

  if (compact) {
    return (
      <div className="mb-4 rounded-lg border border-border bg-canvas px-4 py-3 text-sm">
        <div className="flex flex-wrap gap-2">
          <span className="text-fg-muted">
            FBR: {modeLabel(r.fbr.mode, r.fbr.ready)}
          </span>
          <span className="text-fg-muted">·</span>
          <span className="text-fg-muted">
            PayPro: {modeLabel(r.paypro.mode, r.paypro.ready)}
          </span>
          <span className="text-fg-muted">·</span>
          <span className="text-fg-muted">
            Kuickpay: {modeLabel(r.kuickpay.mode, r.kuickpay.ready)}
          </span>
          <Link href="/settings/integrations" className="ml-auto text-brand hover:underline">
            Integration status
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="mb-6 space-y-4">
      <div className="grid gap-4 md:grid-cols-3">
        <ProviderCard title="FBR / PRAL" provider={r.fbr} docsHref="/settings/fbr-errors" />
        <ProviderCard title="PayPro" provider={r.paypro} docsHref="/settings/online-payments" />
        <ProviderCard title="Kuickpay" provider={r.kuickpay} docsHref="/settings/online-payments" />
      </div>
      {(r.fbr.errorCount ?? 0) > 0 ? (
        <p className="text-sm text-fg-muted">
          {r.fbr.errorCount} FBR error(s), {r.fbr.dueRetryCount ?? 0} due for retry.{" "}
          <Link href="/settings/fbr-errors" className="text-brand hover:underline">
            View queue
          </Link>
        </p>
      ) : null}
      <p className="text-xs text-fg-muted">
        Configure env vars on the API server — see <code className="text-fg">Backend/.env.example</code>.
        Retry worker: {r.fbrRetryWorker ? "enabled" : "disabled"}.
      </p>
    </div>
  );
}
