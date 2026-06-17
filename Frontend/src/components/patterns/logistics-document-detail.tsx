"use client";

import { useRouter } from "next/navigation";
import Decimal from "decimal.js";

import { StatusBadge } from "@/components/app/status-badge";
import { AttachmentPanel } from "@/components/patterns/attachment-panel";
import { PrintLink } from "@/components/print/print-link";
import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { PageHeader } from "@/components/ui/page-header";

export interface LogisticsLine {
  id: string;
  productCode?: string | null;
  quantity: string;
  notes?: string | null;
  [key: string]: unknown;
}

interface LogisticsDocumentDetailProps {
  docLabel: string;
  breadcrumb: string;
  listHref: string;
  voucherNumber: string;
  documentDate: string;
  partyLabel: string;
  partyName: string;
  status: string;
  sourceKind: string;
  sourceId?: string | null;
  notes?: string | null;
  lines: LogisticsLine[];
  printHref?: string;
  attachmentEntityType?: string;
  entityId?: string;
}

function fmtQty(v: string): string {
  try {
    return new Decimal(v).toFixed(2);
  } catch {
    return v;
  }
}

export function LogisticsDocumentDetail({
  docLabel,
  breadcrumb,
  listHref,
  voucherNumber,
  documentDate,
  partyLabel,
  partyName,
  status,
  sourceKind,
  sourceId,
  notes,
  lines,
  printHref,
  attachmentEntityType,
  entityId,
}: LogisticsDocumentDetailProps) {
  const router = useRouter();

  const columns = responsiveListColumns<LogisticsLine>([
    { key: "productCode", header: "Product", render: (r) => r.productCode ?? "—" },
    {
      key: "quantity",
      header: "Quantity",
      align: "right",
      sortable: true,
      sortAccessor: (r) => Number(r.quantity),
      render: (r) => fmtQty(r.quantity),
    },
    { key: "notes", header: "Notes", render: (r) => r.notes ?? "—" },
  ]);

  const totalQty = lines.reduce((acc, l) => {
    try {
      return acc.plus(new Decimal(l.quantity));
    } catch {
      return acc;
    }
  }, new Decimal(0));

  return (
    <div>
      <PageHeader
        title={`${docLabel} ${voucherNumber}`}
        breadcrumb={breadcrumb}
        actions={
          <div className="flex gap-2">
            {printHref ? <PrintLink href={printHref} /> : null}
            <Button type="button" variant="outline" onClick={() => router.push(listHref)}>
              Back
            </Button>
          </div>
        }
      />

      <div className="space-y-4">
        <section className="grid grid-cols-2 gap-4 rounded-lg border border-border bg-surface p-4 md:grid-cols-5">
          <Field label="Voucher" value={voucherNumber} />
          <Field label="Date" value={new Date(documentDate).toLocaleDateString()} />
          <Field label={partyLabel} value={partyName} />
          <div>
            <div className="text-xs font-medium uppercase tracking-wide text-fg-muted">Status</div>
            <div className="mt-1">
              <StatusBadge status={status} />
            </div>
          </div>
          <Field label="Source" value={`${sourceKind}${sourceId ? ` · ${sourceId}` : ""}`} />
          {notes ? <Field label="Notes" value={notes} /> : null}
        </section>

        <section className="overflow-hidden rounded-lg border border-border bg-surface">
          <EnterpriseGrid<LogisticsLine>
            columns={columns}
            rows={lines}
            emptyMessage="No lines on this document."
            getRowId={(r) => r.id}
          />
          {lines.length > 0 ? (
            <div className="flex justify-end border-t border-border px-3 py-2 text-sm font-medium text-fg">
              <span className="text-fg-muted">Total quantity&nbsp;</span>
              <span className="tabular-nums">{totalQty.toFixed(2)}</span>
            </div>
          ) : null}
        </section>

        {attachmentEntityType && entityId ? (
          <AttachmentPanel entityType={attachmentEntityType} entityId={entityId} />
        ) : null}
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
