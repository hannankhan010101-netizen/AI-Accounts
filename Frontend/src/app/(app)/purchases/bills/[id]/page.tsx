/** Supplier bill detail — catalog §6.3. */
"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useState } from "react";

import { StatusBadge } from "@/components/app/status-badge";
import { AttachmentPanel } from "@/components/patterns/attachment-panel";
import {
  DetailAlertBanner,
  DocumentDetailShell,
} from "@/components/patterns/document-detail-shell";
import { DocumentLinesGrid } from "@/components/patterns/document-lines-grid";
import { Button } from "@/components/ui/button";
import { useSupplierNameMap } from "@/lib/hooks/use-party-name-map";
import { purchasesApi } from "@/lib/api/tenant";
import { DetailPageLoading } from "@/components/ui/detail-page-loading";
import { invalidateTenantQueries, useTenantDetailQuery } from "@/lib/api/tenant-query";

export default function SupplierBillDetailPage() {
  const params = useParams<{ id: string }>();
  const queryClient = useQueryClient();
  const supplierNames = useSupplierNameMap();
  const [voidSuccess, setVoidSuccess] = useState(false);
  const { data, isLoading, error } = useTenantDetailQuery(["supplier-bill", params.id], () => purchasesApi.getSupplierBill(params.id), { enabled: !!params.id });

  const approve = useMutation({
    mutationFn: () => purchasesApi.approveSupplierBill(params.id),
    onSuccess: async () => {
      await invalidateTenantQueries(queryClient, "supplier-bills");
      void invalidateTenantQueries(queryClient, "supplier-bill", params.id);
    },
  });
  const voidBill = useMutation({
    mutationFn: () => purchasesApi.voidSupplierBill(params.id),
    onSuccess: async () => {
      setVoidSuccess(true);
      await invalidateTenantQueries(queryClient, "supplier-bills");
      void invalidateTenantQueries(queryClient, "supplier-bill", params.id);
    },
  });

  if (isLoading) return <DetailPageLoading />;
  if (error instanceof Error)
    return (
      <div className="rounded-md border border-status-danger/30 bg-status-danger/10 p-3 text-sm text-status-danger">
        {error.message}
      </div>
    );

  const bill = data?.result;
  if (!bill) return null;

  const status = bill.status ?? "posted";
  const isDraft = status === "draft";
  const isPosted = status === "posted" && !!bill.journalId;
  const isVoided = status === "voided" || status === "reversed";
  const canVoid = isPosted && !isVoided;

  const hasBanners = voidSuccess || voidBill.isError || approve.isError;

  return (
    <DocumentDetailShell
      title={`Bill ${bill.documentNumber ?? bill.id}`}
      breadcrumb="Buy / Bills / Detail"
      metaFields={[
        { label: "Bill no.", value: bill.documentNumber ?? "—" },
        { label: "Date", value: new Date(bill.billDate).toLocaleDateString() },
        {
          label: "Supplier",
          value: supplierNames.get(bill.supplierId) ?? bill.supplierId,
        },
        { label: "Status", value: <StatusBadge status={status} /> },
        {
          label: "GL",
          value: bill.journalId ? (
            <Link
              href={`/settings/journals/${bill.journalId}`}
              className="text-brand hover:underline"
            >
              View journal
            </Link>
          ) : (
            <span className="text-fg-muted">Not posted</span>
          ),
        },
      ]}
      banners={
        hasBanners ? (
          <div className="space-y-2">
            {voidSuccess ? (
              <DetailAlertBanner variant="success">
                Bill voided. GL reversal posted where applicable.
              </DetailAlertBanner>
            ) : null}
            {voidBill.isError ? (
              <DetailAlertBanner variant="error">
                {voidBill.error instanceof Error ? voidBill.error.message : "Void failed"}
              </DetailAlertBanner>
            ) : null}
            {approve.isError ? (
              <DetailAlertBanner variant="error">
                {approve.error instanceof Error ? approve.error.message : "Approve failed"}
              </DetailAlertBanner>
            ) : null}
          </div>
        ) : undefined
      }
      actions={
        <>
          {isDraft ? (
            <>
              <Link
                href={`/purchases/bills/${bill.id}/edit`}
                className="inline-flex h-9 items-center rounded-md border border-border bg-surface px-3 text-sm font-medium text-fg hover:bg-canvas"
              >
                Edit draft
              </Link>
              <Button
                type="button"
                disabled={approve.isPending}
                onClick={() => approve.mutate()}
              >
                {approve.isPending ? "Posting…" : "Approve & post to GL"}
              </Button>
            </>
          ) : null}
          {canVoid ? (
            <Button
              type="button"
              variant="outline"
              disabled={voidBill.isPending}
              onClick={() => {
                if (
                  !window.confirm(
                    "Void this posted bill? GL will be reversed and the document marked void. This cannot be undone.",
                  )
                ) {
                  return;
                }
                voidBill.mutate();
              }}
            >
              {voidBill.isPending ? "Voiding…" : "Void"}
            </Button>
          ) : null}
          {isVoided ? (
            <Link
              href="/purchases/bills/new"
              className="inline-flex h-9 items-center rounded-md border border-border bg-surface px-3 text-sm font-medium text-fg hover:bg-canvas"
            >
              Create replacement
            </Link>
          ) : null}
          <Link
            href={`/print/supplier-bill/${bill.id}`}
            target="_blank"
            className="inline-flex h-9 items-center rounded-md border border-border bg-surface px-3 text-sm font-medium text-brand hover:bg-canvas"
          >
            Print
          </Link>
        </>
      }
    >
      <DocumentLinesGrid
        lines={bill.lines}
        totalAmount={bill.totalAmount}
        showGst
        descriptionDocType="VI"
        showBatchExpiry
        lastRateContext={{
          docType: "VI",
          partyKind: "supplier",
          partyId: bill.supplierId,
        }}
      />

      <AttachmentPanel entityType="supplier_bill" entityId={bill.id} />
    </DocumentDetailShell>
  );
}
