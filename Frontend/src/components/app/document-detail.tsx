"use client";

import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { invalidateTenantQueries, useTenantDetailQuery } from "@/lib/api/tenant-query";
import Decimal from "decimal.js";

import { StatusBadge } from "@/components/app/status-badge";
import { PrintLink } from "@/components/print/print-link";
import { AttachmentPanel } from "@/components/patterns/attachment-panel";
import { DocumentLinesGrid } from "@/components/patterns/document-lines-grid";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { Select } from "@/components/ui/select";
import { ApiError } from "@/lib/api/client";
import type { DocumentLine } from "@/lib/api/tenant";
import type { ProductDescriptionDocType } from "@/lib/hooks/product-description-columns";
import type { LastRateLineContext } from "@/lib/hooks/use-line-last-rate-hints";

function fmt(v: string | number): string {
  try {
    return new Decimal(typeof v === "string" ? v : v.toString()).toFixed(2);
  } catch {
    return String(v);
  }
}

export interface DocumentDetailHeader {
  id: string;
  number: string;
  date: string;
  partyId: string;
  status: string;
  totalAmount: string | number;
}

interface DocumentDetailProps<TDetail extends { lines: DocumentLine[] }> {
  /** Catalog title e.g. "Quotation". */
  docLabel: string;
  /** Path for cancel / back navigation. */
  listHref: string;
  /** Breadcrumb to render in PageHeader. */
  breadcrumb: string;
  /** Allowed status options for the inline Select. */
  statuses: string[];
  /** Convert button copy ("Convert to Sales Order", "Convert to Invoice", etc.). */
  convertLabel?: string;
  /** Route to push to after a successful conversion (e.g. "/sales/orders"). */
  convertSuccessHref?: string;
  /** Status values that allow conversion. */
  convertibleStatuses?: string[];
  /** TanStack Query options. */
  detailQueryKey: readonly unknown[];
  fetchDetail: () => Promise<{ result: TDetail }>;
  /** Header projection. */
  projectHeader: (detail: TDetail) => DocumentDetailHeader;
  /** Mutations. */
  setStatus?: (status: string) => Promise<unknown>;
  convert?: () => Promise<unknown>;
  /** e.g. "Customer" — defaults to "Party". */
  partyLabel?: string;
  /** Resolved display name; falls back to ``partyId`` from header. */
  partyDisplayName?: string;
  /** Derive party label from loaded detail (overrides ``partyDisplayName``). */
  resolvePartyName?: (detail: TDetail) => string | undefined;
  /** Derive last-rate context from loaded detail for view-mode hints. */
  resolveLastRateContext?: (detail: TDetail) => LastRateLineContext | undefined;
  /** Open print view in a new tab when set. */
  printHref?: string;
  /** Force GST columns on the line grid. */
  showGst?: boolean;
  /** Smart Settings product description columns on the line grid. */
  descriptionDocType?: ProductDescriptionDocType;
  /** Last rate view hints on the line grid when Smart Settings view mode is on. */
  lastRateContext?: LastRateLineContext;
  /** When set, show file attachments for this entity. */
  attachmentEntityType?: string;
}

export function DocumentDetail<TDetail extends { lines: DocumentLine[] }>({
  docLabel,
  listHref,
  breadcrumb,
  statuses,
  convertLabel,
  convertSuccessHref,
  convertibleStatuses,
  detailQueryKey,
  fetchDetail,
  projectHeader,
  setStatus,
  convert,
  partyLabel = "Party",
  partyDisplayName,
  resolvePartyName,
  resolveLastRateContext,
  printHref,
  showGst,
  descriptionDocType,
  lastRateContext,
  attachmentEntityType,
}: DocumentDetailProps<TDetail>) {
  const router = useRouter();
  const qc = useQueryClient();
  const [error, setError] = useState<string | null>(null);
  const [convertInfo, setConvertInfo] = useState<string | null>(null);

  const { data, isLoading } = useTenantDetailQuery([...detailQueryKey], fetchDetail);

  const statusMutation = useMutation({
    mutationFn: (status: string) => (setStatus ? setStatus(status) : Promise.resolve()),
    onSuccess: () => {
      setError(null);
      void invalidateTenantQueries(qc, ...detailQueryKey);
    },
    onError: (err) =>
      setError(err instanceof ApiError ? err.message : "Could not update status"),
  });

  const convertMutation = useMutation({
    mutationFn: () => (convert ? convert() : Promise.resolve(null)),
    onSuccess: (res) => {
      setError(null);
      void invalidateTenantQueries(qc, ...detailQueryKey);
      const posted = (res as { posted?: boolean } | null)?.posted;
      if (posted === false) {
        setConvertInfo(
          "Created successfully but no GL journal — set Smart Settings → Defaults to enable posting.",
        );
        setTimeout(() => convertSuccessHref && router.push(convertSuccessHref), 1800);
      } else if (convertSuccessHref) {
        router.push(convertSuccessHref);
      }
    },
    onError: (err) =>
      setError(err instanceof ApiError ? err.message : "Conversion failed"),
  });

  if (isLoading) return <div className="text-sm text-fg-muted">Loading…</div>;
  if (!data) return null;

  const detail = data.result;
  const header = projectHeader(detail);
  const partyName =
    resolvePartyName?.(detail) ?? partyDisplayName ?? header.partyId;
  const resolvedLastRateContext =
    lastRateContext ?? resolveLastRateContext?.(detail);
  const canConvert =
    convertibleStatuses && convertLabel && convert
      ? convertibleStatuses.includes(header.status)
      : false;

  return (
    <div>
      <PageHeader
        title={`${docLabel} ${header.number}`}
        breadcrumb={breadcrumb}
        actions={
          <>
            {printHref ? <PrintLink href={printHref} /> : null}
            <Button type="button" variant="outline" onClick={() => router.push(listHref)}>
              Back
            </Button>
            {canConvert && (
              <Button
                type="button"
                onClick={() => convertMutation.mutate()}
                disabled={convertMutation.isPending}
              >
                {convertMutation.isPending ? "Converting…" : convertLabel}
              </Button>
            )}
          </>
        }
      />

      <div className="space-y-4">
        <section className="grid grid-cols-2 gap-4 rounded-lg border border-border bg-surface p-4 md:grid-cols-5">
          <Field label="Number" value={header.number} />
          <Field label="Date" value={new Date(header.date).toLocaleDateString()} />
          <Field label={partyLabel} value={partyName} />
          <Field label="Total" value={fmt(header.totalAmount)} />
          <div>
            <div className="text-xs font-medium uppercase tracking-wide text-fg-muted">
              Status
            </div>
            <div className="mt-1 flex items-center gap-2">
              <StatusBadge status={header.status} />
              {setStatus && (
                <Select
                  className="h-8 max-w-[10rem]"
                  value={header.status}
                  onChange={(e) => statusMutation.mutate(e.target.value)}
                >
                  {statuses.map((s) => (
                    <option key={s} value={s}>
                      {s.replace(/_/g, " ")}
                    </option>
                  ))}
                </Select>
              )}
            </div>
          </div>
        </section>

        <DocumentLinesGrid
          lines={detail.lines}
          totalAmount={header.totalAmount}
          showGst={showGst}
          descriptionDocType={descriptionDocType}
          lastRateContext={resolvedLastRateContext}
        />

        {attachmentEntityType ? (
          <AttachmentPanel
            entityType={attachmentEntityType}
            entityId={header.id}
          />
        ) : null}

        {error && (
          <div className="rounded-md border border-status-danger/30 bg-status-danger/10 px-3 py-2 text-sm text-status-danger">
            {error}
          </div>
        )}
        {convertInfo && (
          <div className="rounded-md border border-status-warning/30 bg-status-warning/10 px-3 py-2 text-sm text-status-warning">
            {convertInfo}
          </div>
        )}
      </div>
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
