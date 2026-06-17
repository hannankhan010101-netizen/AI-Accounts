"use client";

import { useRouter } from "next/navigation";
import Decimal from "decimal.js";

import { PrintLink } from "@/components/print/print-link";
import { StatusBadge } from "@/components/app/status-badge";
import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { PageHeader } from "@/components/ui/page-header";

export interface InventoryLine {
  id: string;
  productCode: string;
  quantity?: string;
  quantityDelta?: string;
  locationCode?: string | null;
  unitCost?: string;
  [key: string]: unknown;
}

interface InventoryVoucherDetailProps {
  docLabel: string;
  breadcrumb: string;
  listHref: string;
  voucherNumber: string;
  documentDate: string;
  status: string;
  fields: { label: string; value: string }[];
  lines: InventoryLine[];
  lineColumns: GridColumn<InventoryLine>[];
  notes?: string | null;
  printHref: string;
}

export function InventoryVoucherDetail({
  docLabel,
  breadcrumb,
  listHref,
  voucherNumber,
  documentDate,
  status,
  fields,
  lines,
  lineColumns,
  notes,
  printHref,
}: InventoryVoucherDetailProps) {
  const router = useRouter();

  return (
    <div>
      <PageHeader
        title={`${docLabel} ${voucherNumber}`}
        breadcrumb={breadcrumb}
        actions={
          <div className="flex gap-2">
            <PrintLink href={printHref} />
            <Button type="button" variant="outline" onClick={() => router.push(listHref)}>
              Back
            </Button>
          </div>
        }
      />

      <div className="space-y-4">
        <section className="grid grid-cols-2 gap-4 rounded-lg border border-border bg-surface p-4 md:grid-cols-4">
          <Field label="Voucher" value={voucherNumber} />
          <Field label="Date" value={new Date(documentDate).toLocaleDateString()} />
          {fields.map((f) => (
            <Field key={f.label} label={f.label} value={f.value} />
          ))}
          <div>
            <div className="text-xs font-medium uppercase tracking-wide text-fg-muted">Status</div>
            <div className="mt-1">
              <StatusBadge status={status} />
            </div>
          </div>
          {notes ? <Field label="Notes" value={notes} /> : null}
        </section>

        <EnterpriseGrid<InventoryLine>
          columns={lineColumns}
          rows={lines}
          emptyMessage="No lines."
          getRowId={(r) => r.id}
        />
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

function fmtQty(v: string | undefined): string {
  if (!v) return "—";
  try {
    return new Decimal(v).toFixed(2);
  } catch {
    return v;
  }
}

export { fmtQty };
