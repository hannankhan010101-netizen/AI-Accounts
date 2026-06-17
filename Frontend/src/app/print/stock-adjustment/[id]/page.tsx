"use client";

import { useParams } from "next/navigation";
import Decimal from "decimal.js";

import { PrintQueryShell } from "@/components/print/print-query-shell";
import { VoucherPrint } from "@/components/print/voucher-print";
import { useVoucherPrintPage } from "@/lib/hooks/use-voucher-print-page";
import { inventoryWritesApi } from "@/lib/api/tenant";

function fmtQty(v: string): string {
  try {
    return new Decimal(v).toFixed(2);
  } catch {
    return v;
  }
}

export default function StockAdjustmentPrintPage() {
  const params = useParams<{ id: string }>();

  const { query, businessName, businessAddress, businessLogoUrl, template, isLoading, error } = useVoucherPrintPage(
    ["print-stock-adjustment", params.id],
    () => inventoryWritesApi.getStockAdjustment(params.id),
    !!params.id,
  
    "stock-adjustment",
  );

  const doc = query.data?.result;
  const lines = doc?.lines ?? [];

  return (
    <PrintQueryShell
      isLoading={isLoading}
      error={error}
      ready={Boolean(doc)}
      notFoundMessage="Adjustment not found."
    >
      {doc ? (
        <VoucherPrint
          title="Stock Adjustment"
          documentNumber={doc.voucherNumber}
          documentDate={doc.adjustmentDate}
          businessName={businessName}
          businessAddress={businessAddress}
          businessLogoUrl={businessLogoUrl}
          template={template}
          fields={[
            { label: "Reason", value: doc.reason },
            { label: "Status", value: doc.status },
          ]}
          tableHeaders={["Product", "Location", "Qty Δ", "Unit cost"]}
          tableRows={lines.map((l) => [
            l.productCode,
            l.locationCode ?? "—",
            fmtQty(l.quantityDelta),
            l.unitCost,
          ])}
          notes={doc.notes ?? undefined}
        />
      ) : null}
    </PrintQueryShell>
  );
}
