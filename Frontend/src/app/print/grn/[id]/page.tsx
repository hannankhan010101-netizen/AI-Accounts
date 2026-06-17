"use client";

import { useParams } from "next/navigation";
import Decimal from "decimal.js";

import { PrintQueryShell } from "@/components/print/print-query-shell";
import { VoucherPrint } from "@/components/print/voucher-print";
import { useSupplierNameMap } from "@/lib/hooks/use-party-name-map";
import { useVoucherPrintPage } from "@/lib/hooks/use-voucher-print-page";
import { deliveryApi } from "@/lib/api/tenant";

function fmtQty(v: string): string {
  try {
    return new Decimal(v).toFixed(2);
  } catch {
    return v;
  }
}

export default function GrnPrintPage() {
  const params = useParams<{ id: string }>();
  const supplierNames = useSupplierNameMap();

  const { query, businessName, businessAddress, businessLogoUrl, template, isLoading, error } = useVoucherPrintPage(
    ["print-grn", params.id],
    () => deliveryApi.getGrn(params.id),
    !!params.id,
  
    "grnpo",
  );

  const grn = query.data?.result;
  const lines = grn?.lines ?? [];

  return (
    <PrintQueryShell
      isLoading={isLoading}
      error={error}
      ready={Boolean(grn)}
      notFoundMessage="GRN not found."
    >
      {grn ? (
        <VoucherPrint
          title="Goods Receipt Note"
          documentNumber={grn.voucherNumber}
          documentDate={grn.receiptDate}
          businessName={businessName}
          businessAddress={businessAddress}
          businessLogoUrl={businessLogoUrl}
          template={template}
          fields={[
            {
              label: "Supplier",
              value: supplierNames.get(grn.supplierId) ?? grn.supplierId,
            },
            { label: "Status", value: grn.status },
            {
              label: "Source",
              value: `${grn.sourceKind}${grn.sourceId ? ` · ${grn.sourceId}` : ""}`,
            },
          ]}
          tableHeaders={["Product", "Quantity", "Notes"]}
          tableRows={lines.map((l) => [
            l.productCode ?? "—",
            fmtQty(l.quantity),
            l.notes ?? "",
          ])}
          notes={(grn as { notes?: string | null }).notes ?? undefined}
        />
      ) : null}
    </PrintQueryShell>
  );
}
