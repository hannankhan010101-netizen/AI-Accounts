/** FBR submission errors and retry queue — P8. */
"use client";
import { useTenantListQuery, invalidateTenantQueries } from "@/lib/api/tenant-query";


import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { IntegrationReadinessBanner } from "@/components/settings/integration-readiness-banner";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { WorkspaceLoading } from "@/components/ui/workspace-loading";
import { fbrApi } from "@/lib/api/tenant";
import { brandLinkClasses } from "@/lib/design-tokens/brand-surfaces";
import { cn } from "@/lib/utils";

type ErrorRow = Record<string, unknown> & {
  id?: string;
  salesInvoiceId?: string;
  status?: string;
  lastError?: string | null;
  retryCount?: number;
  nextRetryAt?: string | null;
};

export default function FbrErrorsPage() {
  const qc = useQueryClient();
  const { data, isLoading, error } = useTenantListQuery(["fbr-errors"], () => fbrApi.listErrors());

  const queueRetries = useMutation({
    mutationFn: () => fbrApi.retryPending(),
    onSuccess: () => {
      void invalidateTenantQueries(qc, "fbr-errors");
    },
  });

  const rows = (data?.result ?? []) as ErrorRow[];

  return (
    <div>
      <PageHeader
        title="FBR submission errors"
        breadcrumb="Settings / FBR errors"
        description="Failed or pending PRAL submissions. Retry individually from the invoice or queue all due retries."
        actions={
          <Button
            type="button"
            disabled={queueRetries.isPending}
            onClick={() => queueRetries.mutate()}
          >
            {queueRetries.isPending ? "Queueing…" : "Queue due retries"}
          </Button>
        }
      />
      <IntegrationReadinessBanner />
      {error instanceof Error ? (
        <p className="text-sm text-status-danger">{error.message}</p>
      ) : null}
      {isLoading ? (
        <WorkspaceLoading />
      ) : rows.length === 0 ? (
        <p className="text-sm text-fg-muted">No FBR errors.</p>
      ) : (
        <ul className="divide-y rounded-lg border border-border bg-surface text-sm">
          {rows.map((row) => (
            <li key={row.id} className="px-4 py-3">
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div>
                  <Link
                    href={`/sales/invoices/${row.salesInvoiceId}`}
                    className={cn("font-medium hover:underline", brandLinkClasses)}
                  >
                    Invoice {row.salesInvoiceId}
                  </Link>
                  <p className="mt-1 text-fg-muted">
                    Status: {row.status} · Retries: {row.retryCount ?? 0}
                  </p>
                  {row.lastError ? (
                    <p className="mt-1 text-status-danger">{row.lastError}</p>
                  ) : null}
                  {row.nextRetryAt ? (
                    <p className="mt-1 text-xs text-fg-muted">
                      Next retry: {new Date(String(row.nextRetryAt)).toLocaleString()}
                    </p>
                  ) : null}
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
