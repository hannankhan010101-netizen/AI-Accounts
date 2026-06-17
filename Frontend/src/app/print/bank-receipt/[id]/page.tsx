"use client";

import { useParams } from "next/navigation";
import Decimal from "decimal.js";

import { PrintQueryShell } from "@/components/print/print-query-shell";
import { VoucherPrint } from "@/components/print/voucher-print";
import { useBankAccountNameMap } from "@/lib/hooks/use-bank-account-name-map";
import { useVoucherPrintPage } from "@/lib/hooks/use-voucher-print-page";
import { bankApi } from "@/lib/api/tenant";

function fmt(v: string | number | undefined | null): string {
  if (v == null || v === "") return "—";
  try {
    return new Decimal(typeof v === "string" ? v : v.toString()).toFixed(2);
  } catch {
    return String(v);
  }
}

export default function BankReceiptPrintPage() {
  const params = useParams<{ id: string }>();
  const bankNames = useBankAccountNameMap();

  const { query, businessName, businessAddress, businessLogoUrl, template, isLoading, error } = useVoucherPrintPage(
    ["print-bank-receipt", params.id],
    () => bankApi.getReceipt(params.id),
    !!params.id,
  
    "bank",
  );

  const rec = query.data?.result;

  return (
    <PrintQueryShell
      isLoading={isLoading}
      error={error}
      ready={Boolean(rec)}
      notFoundMessage="Receipt not found."
    >
      {rec ? (
        <VoucherPrint
          title="Bank Receipt"
          documentNumber={String(rec.voucherNumber ?? rec.id.slice(0, 8))}
          documentDate={rec.receiptDate}
          businessName={businessName}
          businessAddress={businessAddress}
          businessLogoUrl={businessLogoUrl}
          template={template}
          fields={[
            {
              label: "Bank account",
              value: bankNames.get(rec.bankAccountId) ?? rec.bankAccountId,
            },
            { label: "Amount", value: fmt(rec.totalAmount) },
            {
              label: "Nominal",
              value: (rec as { nominalCode?: string | null }).nominalCode ?? "—",
            },
            { label: "Posted", value: rec.journalId ? "Yes" : "No" },
          ]}
        />
      ) : null}
    </PrintQueryShell>
  );
}
