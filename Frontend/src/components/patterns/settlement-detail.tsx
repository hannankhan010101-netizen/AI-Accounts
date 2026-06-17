"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { invalidateTenantQueries, useTenantDetailQuery } from "@/lib/api/tenant-query";
import { useMemo, useState } from "react";
import Decimal from "decimal.js";

import {
  AllocationPicker,
  type AllocationRow,
} from "@/components/app/allocation-picker";
import { AttachmentPanel } from "@/components/patterns/attachment-panel";
import { StatusBadge } from "@/components/app/status-badge";
import { PrintLink } from "@/components/print/print-link";
import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { PageHeader } from "@/components/ui/page-header";
import { readPaymentMethod } from "@/components/app/payment-method-field";
import { ApiError } from "@/lib/api/client";
import type { AdvanceReturnRow, SettlementBalance } from "@/lib/api/tenant";
import { opMethodLabel } from "@/lib/settings/op-methods-catalog";

export interface SettlementAllocation {
  id: string;
  documentId: string;
  amount: string;
  [key: string]: unknown;
}

export interface SettlementDoc {
  id: string;
  voucherNumber?: string | null;
  receiptNumber?: string | null;
  paymentDate?: string;
  receiptDate?: string;
  customerId?: string;
  supplierId?: string;
  bankAccountId: string;
  totalAmount: string | number;
  journalId?: string | null;
  status?: string;
  customFields?: Record<string, unknown> | null;
}

interface SettlementDetailProps {
  docLabel: string;
  breadcrumb: string;
  listHref: string;
  queryKey: readonly unknown[];
  fetchDetail: () => Promise<{
    result: SettlementDoc;
    allocations: unknown[];
    balance?: SettlementBalance;
    advanceReturns?: AdvanceReturnRow[];
  }>;
  mapAllocation: (raw: {
    id: string;
    salesInvoiceId?: string;
    supplierBillId?: string;
    amount: string;
  }) => SettlementAllocation;
  partyLabel: string;
  resolvePartyName: (doc: SettlementDoc) => string;
  resolveBankName: (doc: SettlementDoc) => string;
  resolvePartyId: (doc: SettlementDoc) => string;
  pickerMode: "customer" | "supplier";
  documentLinkPrefix: string;
  documentColumnHeader: string;
  resolveDocumentLabel: (documentId: string) => string;
  allocate: (id: string, body: Record<string, unknown>) => Promise<unknown>;
  settlementId: string;
  printHref?: string;
  attachmentEntityType?: "sales_receipt" | "supplier_payment";
  returnAdvanceHref?: string;
  /** Post draft settlement to GL (import / template workflow). */
  postToGl?: (id: string) => Promise<unknown>;
}

function fmtMoney(v: string | number): string {
  try {
    return new Decimal(typeof v === "string" ? v : v.toString()).toFixed(2);
  } catch {
    return String(v);
  }
}

export function SettlementDetail({
  docLabel,
  breadcrumb,
  listHref,
  queryKey,
  fetchDetail,
  mapAllocation,
  partyLabel,
  resolvePartyName,
  resolveBankName,
  resolvePartyId,
  pickerMode,
  documentLinkPrefix,
  documentColumnHeader,
  resolveDocumentLabel,
  allocate,
  settlementId,
  printHref,
  attachmentEntityType,
  returnAdvanceHref,
  postToGl,
}: SettlementDetailProps) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [allocations, setAllocations] = useState<AllocationRow[]>([]);

  const { data, isLoading, error } = useTenantDetailQuery(
    [...queryKey],
    async () => {
      const res = await fetchDetail();
      return {
        ...res,
        allocations: (res.allocations ?? []).map((a) =>
          mapAllocation(
            a as {
              id: string;
              salesInvoiceId?: string;
              supplierBillId?: string;
              amount: string;
            },
          ),
        ) as SettlementAllocation[],
        balance: res.balance,
        advanceReturns: res.advanceReturns,
      };
    },
    { enabled: Boolean(settlementId) },
  );

  const postGlMutation = useMutation({
    mutationFn: () => postToGl!(settlementId),
    onSuccess: () => {
      void invalidateTenantQueries(queryClient, ...queryKey);
    },
  });

  const allocateMutation = useMutation({
    mutationFn: () => {
      const payload =
        pickerMode === "customer"
          ? {
              autoFifo: false,
              allocations: allocations
                .filter((a) => a.amount && Number(a.amount) > 0)
                .map((a) => ({ invoiceId: a.documentId, amount: a.amount })),
            }
          : {
              autoFifo: false,
              allocations: allocations
                .filter((a) => a.amount && Number(a.amount) > 0)
                .map((a) => ({ billId: a.documentId, amount: a.amount })),
            };
      return allocate(settlementId, payload);
    },
    onSuccess: () => {
      void invalidateTenantQueries(queryClient, ...queryKey);
      setAllocations([]);
    },
  });

  const summary = useMemo(() => {
    const existing = data?.allocations ?? [];
    const totalAllocated = data?.balance
      ? Number(data.balance.allocated)
      : existing.reduce((sum, a) => sum + Number(a.amount), 0);
    const returned = data?.balance ? Number(data.balance.returned) : 0;
    const total = Number(data?.result?.totalAmount ?? 0);
    const unallocated = data?.balance
      ? Number(data.balance.unallocated)
      : total - totalAllocated;
    return {
      totalAllocated,
      returned,
      unallocated,
      showPicker: unallocated > 0.01,
    };
  }, [data]);

  if (isLoading) return <div className="text-sm text-fg-muted">Loading…</div>;
  if (error instanceof Error)
    return (
      <div className="rounded-md border border-status-danger/30 bg-status-danger/10 p-3 text-sm text-status-danger">
        {error.message}
      </div>
    );

  const doc = data?.result;
  if (!doc) return null;

  const partyName = resolvePartyName(doc);
  const bankName = resolveBankName(doc);
  const partyId = resolvePartyId(doc);

  const voucher =
    doc.voucherNumber ?? doc.receiptNumber ?? doc.id.slice(0, 8);
  const date = doc.paymentDate ?? doc.receiptDate ?? "";
  const paymentMethodId = readPaymentMethod(doc.customFields);
  const paymentMethodLabel = paymentMethodId ? opMethodLabel(paymentMethodId) : null;

  const allocColumns: GridColumn<SettlementAllocation>[] = [
    {
      key: "documentId",
      header: documentColumnHeader,
      render: (r) => (
        <Link href={`${documentLinkPrefix}/${r.documentId}`} className="text-brand hover:underline">
          {resolveDocumentLabel(r.documentId)}
        </Link>
      ),
    },
    {
      key: "amount",
      header: "Amount",
      align: "right",
      sortable: true,
      sortAccessor: (r) => Number(r.amount),
      render: (r) => fmtMoney(r.amount),
    },
  ];

  return (
    <div>
      <PageHeader
        title={`${docLabel} ${voucher}`}
        breadcrumb={breadcrumb}
        actions={
          <div className="flex flex-wrap gap-2">
            {postToGl && !doc.journalId && (doc.status ?? "").toLowerCase() === "draft" ? (
              <Button
                type="button"
                disabled={postGlMutation.isPending}
                onClick={() => postGlMutation.mutate()}
              >
                {postGlMutation.isPending ? "Posting…" : "Post to GL"}
              </Button>
            ) : null}
            {returnAdvanceHref && summary.unallocated > 0.01 ? (
              <Button type="button" onClick={() => router.push(returnAdvanceHref)}>
                Return advance
              </Button>
            ) : null}
            {printHref ? (
              <>
                <PrintLink href={printHref} />
                <PrintLink href={`${printHref}?copies=2`} label="Two copies" />
              </>
            ) : null}
            <Button type="button" variant="outline" onClick={() => router.push(listHref)}>
              Back
            </Button>
          </div>
        }
      />

      <section className="mb-4 grid grid-cols-1 gap-4 rounded-lg border border-border bg-surface p-4 md:grid-cols-6">
        <Field label="Date" value={date ? new Date(date).toLocaleDateString() : "—"} />
        <Field label={partyLabel} value={partyName} />
        <Field label="Bank account" value={bankName} />
        <Field label="Amount" value={fmtMoney(doc.totalAmount)} />
        {paymentMethodLabel ? <Field label="Payment method" value={paymentMethodLabel} /> : null}
        <div>
          <div className="text-xs font-medium uppercase tracking-wide text-fg-muted">Posted</div>
          <div className="mt-1 flex flex-col gap-1">
            <StatusBadge status={doc.journalId ? "posted" : "draft"} />
            {doc.journalId ? (
              <Link
                href={`/settings/journals/${doc.journalId}`}
                className="text-sm text-brand hover:underline"
              >
                View journal
              </Link>
            ) : (
              <span className="text-sm text-fg-muted">No GL journal</span>
            )}
          </div>
        </div>
      </section>

      <section className="rounded-lg border border-border bg-surface p-4">
        <h2 className="text-sm font-semibold text-fg">Allocations</h2>
        <p className="mt-1 text-sm text-fg-muted">
          Allocated {summary.totalAllocated.toFixed(2)}
          {summary.returned > 0 ? ` · Returned ${summary.returned.toFixed(2)}` : ""}
          {" · Unallocated "}
          {summary.unallocated.toFixed(2)}
        </p>

        <div className="mt-3">
          <EnterpriseGrid<SettlementAllocation>
            columns={allocColumns}
            rows={data?.allocations ?? []}
            emptyMessage="No allocations recorded yet."
            getRowId={(r) => r.id}
          />
        </div>

        {summary.showPicker ? (
          <div className="mt-6 border-t border-border pt-4">
            <h3 className="text-sm font-medium text-fg">Allocate balance</h3>
            <p className="mt-1 text-xs text-fg-muted">
              Match this settlement to open {pickerMode === "customer" ? "invoices" : "bills"}.
            </p>
            <div className="mt-3">
              <AllocationPicker
                mode={pickerMode}
                partyId={partyId}
                receiptTotal={String(summary.unallocated)}
                rows={allocations}
                onChange={setAllocations}
              />
            </div>
            <Button
              type="button"
              className="mt-3"
              disabled={allocateMutation.isPending || allocations.length === 0}
              onClick={() => allocateMutation.mutate()}
            >
              {allocateMutation.isPending ? "Saving…" : "Apply allocation"}
            </Button>
            {allocateMutation.isError ? (
              <p className="mt-2 text-sm text-status-danger">
                {allocateMutation.error instanceof ApiError
                  ? allocateMutation.error.message
                  : "Allocation failed"}
              </p>
            ) : null}
          </div>
        ) : null}
      </section>

      {attachmentEntityType ? (
        <AttachmentPanel
          entityType={attachmentEntityType}
          entityId={settlementId}
          title="Attachments"
        />
      ) : null}
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs font-medium uppercase tracking-wide text-fg-muted">{label}</div>
      <div className="mt-1 text-sm font-medium text-fg">{value}</div>
    </div>
  );
}
