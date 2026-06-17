"use client";

import { useParams, useSearchParams } from "next/navigation";
import Decimal from "decimal.js";

import { PrintQueryShell } from "@/components/print/print-query-shell";
import { VoucherPrint } from "@/components/print/voucher-print";
import { useBankAccountNameMap } from "@/lib/hooks/use-bank-account-name-map";
import { useCustomerNameMap } from "@/lib/hooks/use-party-name-map";
import { useInvoiceNumberMap } from "@/lib/hooks/use-document-number-map";
import { useVoucherPrintPage } from "@/lib/hooks/use-voucher-print-page";
import { salesApi } from "@/lib/api/tenant";

function fmt(v: string | number): string {
  try {
    return new Decimal(typeof v === "string" ? v : v.toString()).toFixed(2);
  } catch {
    return String(v);
  }
}

export default function SalesReceiptPrintPage() {
  const params = useParams<{ id: string }>();
  const searchParams = useSearchParams();
  const forceTwoCopies = searchParams.get("copies") === "2";
  const customerNames = useCustomerNameMap();
  const bankNames = useBankAccountNameMap();
  const invoiceNumbers = useInvoiceNumberMap();

  const { query, businessName, businessAddress, businessLogoUrl, template, isLoading, error } = useVoucherPrintPage(
    ["print-sales-receipt", params.id],
    () => salesApi.getReceipt(params.id),
    !!params.id,
    "sr",
  );

  const rec = query.data?.result;
  const allocations = query.data?.allocations ?? [];

  return (
    <PrintQueryShell
      isLoading={isLoading}
      error={error}
      ready={Boolean(rec)}
      notFoundMessage="Receipt not found."
    >
      {rec ? (
        <VoucherPrint
          title="Sales Receipt"
          documentNumber={String(rec.receiptNumber ?? rec.id.slice(0, 8))}
          documentDate={rec.receiptDate}
          businessName={businessName}
          businessAddress={businessAddress}
          businessLogoUrl={businessLogoUrl}
          fields={[
            {
              label: "Customer",
              value: customerNames.get(rec.customerId ?? "") ?? rec.customerId ?? "—",
            },
            {
              label: "Bank account",
              value: bankNames.get(rec.bankAccountId) ?? rec.bankAccountId,
            },
            { label: "Amount", value: fmt(rec.totalAmount) },
            { label: "Status", value: rec.status ?? "—" },
          ]}
          tableHeaders={["Invoice", "Allocated"]}
          tableRows={allocations.map((a) => [
            invoiceNumbers.get(a.salesInvoiceId ?? "") ?? a.salesInvoiceId ?? "—",
            fmt(a.amount),
          ])}
          template={
            template
              ? { ...template, twoCopies: template.twoCopies || forceTwoCopies }
              : forceTwoCopies
                ? { twoCopies: true }
                : template
          }
        />
      ) : null}
    </PrintQueryShell>
  );
}
