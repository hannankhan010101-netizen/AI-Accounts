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

export default function StockTransferPrintPage() {
  const params = useParams<{ id: string }>();

  const { query, businessName, businessAddress, businessLogoUrl, template, isLoading, error } = useVoucherPrintPage(
    ["print-stock-transfer", params.id],
    () => inventoryWritesApi.getStockTransfer(params.id),
    !!params.id,
  
    "stock-transfer",
  );

  const doc = query.data?.result;
  const lines = doc?.lines ?? [];

  return (
    <PrintQueryShell
      isLoading={isLoading}
      error={error}
      ready={Boolean(doc)}
      notFoundMessage="Transfer not found."
    >
      {doc ? (
        <VoucherPrint
          title="Stock Transfer"
          documentNumber={doc.voucherNumber}
          documentDate={doc.transferDate}
          businessName={businessName}
          businessAddress={businessAddress}
          businessLogoUrl={businessLogoUrl}
          template={template}
          fields={[
            { label: "From", value: doc.fromLocationCode },
            { label: "To", value: doc.toLocationCode },
            { label: "Status", value: doc.status },
          ]}
          tableHeaders={["Product", "Quantity", "Unit cost"]}
          tableRows={lines.map((l) => [l.productCode, fmtQty(l.quantity), l.unitCost])}
          notes={doc.notes ?? undefined}
        />
      ) : null}
    </PrintQueryShell>
  );
}
