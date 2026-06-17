"use client";

import Decimal from "decimal.js";

import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import type { DocumentLine } from "@/lib/api/tenant";
import {
  lineDescriptionCellValue,
  type ProductDescriptionDocType,
} from "@/lib/hooks/product-description-columns";
import { useProductDescriptionColumns } from "@/lib/hooks/use-product-description-columns";
import {
  useLineLastRateHints,
  type LastRateLineContext,
} from "@/lib/hooks/use-line-last-rate-hints";

function fmt(v: string | number | undefined | null): string {
  if (v === undefined || v === null || v === "") return "—";
  try {
    return new Decimal(typeof v === "string" ? v : v.toString()).toFixed(2);
  } catch {
    return String(v);
  }
}

function fmtDate(v: unknown): string {
  if (typeof v !== "string" || !v.trim()) return "—";
  try {
    return new Date(v).toLocaleDateString();
  } catch {
    return v;
  }
}

export interface DocumentLinesGridProps {
  lines: DocumentLine[];
  totalAmount: string | number;
  showProject?: boolean;
  showGst?: boolean;
  /** Smart Settings product description columns (§12.2.5). */
  descriptionDocType?: ProductDescriptionDocType;
  showBatchExpiry?: boolean;
  /** When set and view mode is on, show last-rate hints under the rate column. */
  lastRateContext?: LastRateLineContext;
}

/** Read-only line grid for sales/purchase document detail screens. */
export function DocumentLinesGrid({
  lines,
  totalAmount,
  showProject = false,
  showGst,
  descriptionDocType,
  showBatchExpiry = false,
  lastRateContext,
}: DocumentLinesGridProps) {
  const { columns: descriptionColumns } = useProductDescriptionColumns(
    descriptionDocType ?? "SI",
  );
  const activeDescriptionColumns = descriptionDocType ? descriptionColumns : [];
  const productCodes = lines.map((l) => (typeof l.productCode === "string" ? l.productCode : ""));
  const lastRateHints = useLineLastRateHints(productCodes, lastRateContext);

  const gstVisible =
    showGst ??
    lines.some(
      (l) => l.gstCode || (l.taxAmount !== undefined && Number(l.taxAmount) > 0),
    );

  const batchVisible =
    showBatchExpiry ||
    lines.some(
      (l) =>
        (typeof l.batchNumber === "string" && l.batchNumber.trim()) ||
        (typeof l.expiryDate === "string" && l.expiryDate.trim()),
    );

  const columns = responsiveListColumns<DocumentLine>([
    { key: "productCode", header: "Product", render: (r) => r.productCode ?? "—" },
    ...activeDescriptionColumns.map(
      (col): GridColumn<DocumentLine> => ({
        key: col.fieldKey,
        header: col.header,
        render: (r) => lineDescriptionCellValue(r as Record<string, unknown>, col.fieldKey),
      }),
    ),
    {
      key: "quantity",
      header: "Quantity",
      align: "right",
      render: (r) => fmt(r.quantity),
    },
    { key: "rate", header: "Rate", align: "right", render: (r) => {
      const code = typeof r.productCode === "string" ? r.productCode : "";
      const hint = code ? lastRateHints.get(code) : undefined;
      return (
        <div className="text-right">
          <div className="tabular-nums">{fmt(r.rate)}</div>
          {hint ? <div className="text-xs font-normal text-fg-muted">{hint}</div> : null}
        </div>
      );
    } },
  ]);

  if (batchVisible) {
    columns.push(
      {
        key: "batchNumber",
        header: "Batch",
        render: (r) =>
          typeof r.batchNumber === "string" && r.batchNumber.trim()
            ? r.batchNumber
            : "—",
      },
      {
        key: "expiryDate",
        header: "Expiry",
        render: (r) => fmtDate(r.expiryDate),
      },
    );
  }

  if (gstVisible) {
    columns.push(
      { key: "gstCode", header: "GST", render: (r) => r.gstCode ?? "—" },
      {
        key: "taxAmount",
        header: "Tax",
        align: "right",
        render: (r) => (r.taxAmount !== undefined ? fmt(r.taxAmount) : "—"),
      },
    );
  }

  columns.push({
    key: "lineTotal",
    header: "Line total",
    align: "right",
    render: (r) => fmt(r.lineTotal),
  });

  if (showProject) {
    columns.push({
      key: "projectCode",
      header: "Project",
      render: (r) => r.projectCode ?? "—",
    });
  }

  return (
    <section className="overflow-hidden rounded-lg border border-border bg-surface">
      <EnterpriseGrid<DocumentLine>
        columns={columns}
        rows={lines}
        emptyMessage="No lines."
        getRowId={(r) => r.id}
      />
      {lines.length > 0 ? (
        <div className="flex justify-end border-t border-border px-3 py-2 text-sm font-medium text-fg">
          <span className="text-fg-muted">Total&nbsp;</span>
          <span className="tabular-nums">{fmt(totalAmount)}</span>
        </div>
      ) : null}
    </section>
  );
}
