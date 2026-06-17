/** Bank reconciliation session detail — catalog §4.5 */
"use client";
import { invalidateTenantQueries, useTenantDetailQuery } from "@/lib/api/tenant-query";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { BankReconciliationWorkspace } from "@/components/app/bank-reconciliation-workspace";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { bankApi } from "@/lib/api/tenant";
import { ApiError } from "@/lib/api/client";

import { WorkspaceLoading } from "@/components/ui/workspace-loading";

export default function BankReconciliationDetailPage() {
  const params = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const { data, isLoading, error } = useTenantDetailQuery(["bank-reconciliation", params.id], () => bankApi.getReconciliation(params.id), { enabled: Boolean(params.id) });

  const clearItems = useMutation({
    mutationFn: ({ itemIds, cleared }: { itemIds: string[]; cleared: boolean }) =>
      bankApi.clearReconciliationItems(params.id, { itemIds, cleared }),
    onSuccess: () => {
      void invalidateTenantQueries(queryClient, "bank-reconciliation", params.id);
    },
  });

  const autoMatch = useMutation({
    mutationFn: () => bankApi.autoMatchReconciliation(params.id),
    onSuccess: () => {
      void invalidateTenantQueries(queryClient, "bank-reconciliation", params.id);
    },
  });

  const complete = useMutation({
    mutationFn: () => bankApi.completeReconciliation(params.id),
    onSuccess: () => {
      void invalidateTenantQueries(queryClient, "bank-reconciliation", params.id);
      void invalidateTenantQueries(queryClient, "bank-reconciliations");
    },
  });

  const s = data?.result;
  const isOpen = s?.status === "open";
  const actionError =
    (clearItems.error instanceof ApiError && clearItems.error.message) ||
    (complete.error instanceof Error && complete.error.message) ||
    null;

  return (
    <div>
      <PageHeader
        title="Bank reconciliation"
        breadcrumb="Money / Reconciliation"
        actions={
          <div className="flex gap-2">
            {isOpen && (
              <>
                <Button
                  type="button"
                  variant="secondary"
                  disabled={autoMatch.isPending}
                  onClick={() => autoMatch.mutate()}
                >
                  {autoMatch.isPending ? "Matching…" : "Auto-match by amount"}
                </Button>
                <Button
                type="button"
                disabled={complete.isPending}
                onClick={() => {
                  if (
                    window.confirm(
                      "Complete this reconciliation? Cleared items will be finalized for this statement.",
                    )
                  ) {
                    complete.mutate();
                  }
                }}
              >
                {complete.isPending ? "Completing…" : "Complete"}
              </Button>
              </>
            )}
            <Link href="/bank/reconciliation">
              <Button variant="outline">Back</Button>
            </Link>
          </div>
        }
      />

      {actionError && (
        <p className="mb-4 text-sm text-status-danger" role="alert">
          {actionError}
        </p>
      )}

      {isLoading ? <WorkspaceLoading className="mt-4" /> : null}
      {error instanceof Error ? (
        <p className="mt-4 text-sm text-status-danger" role="alert">
          {error.message}
        </p>
      ) : null}

      {!isLoading && s ? (
        <>
          <dl className="mb-4 grid max-w-2xl gap-2 rounded-lg border border-border bg-surface p-4 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-fg-muted">Status</dt>
              <dd className="font-medium capitalize">{s.status}</dd>
            </div>
            <div>
              <dt className="text-fg-muted">Statement date</dt>
              <dd>{new Date(String(s.statementDate)).toLocaleDateString()}</dd>
            </div>
            <div>
              <dt className="text-fg-muted">Statement balance</dt>
              <dd className="tabular-nums">{String(s.statementBalance)}</dd>
            </div>
            <div>
              <dt className="text-fg-muted">Bank account</dt>
              <dd className="font-mono text-xs">{String(s.bankAccountId)}</dd>
            </div>
          </dl>

          <BankReconciliationWorkspace
            session={s}
            isOpen={isOpen}
            isUpdating={clearItems.isPending}
            onToggleCleared={(itemIds, cleared) => clearItems.mutate({ itemIds, cleared })}
          />
        </>
      ) : null}
    </div>
  );
}
