"use client";

import { useParams, useSearchParams } from "next/navigation";
import Decimal from "decimal.js";

import { PrintQueryShell } from "@/components/print/print-query-shell";
import { VoucherPrint } from "@/components/print/voucher-print";
import { useBankAccountNameMap } from "@/lib/hooks/use-bank-account-name-map";
import { useBillNumberMap } from "@/lib/hooks/use-document-number-map";
import { useSupplierNameMap } from "@/lib/hooks/use-party-name-map";
import { useVoucherPrintPage } from "@/lib/hooks/use-voucher-print-page";
import { purchasesApi } from "@/lib/api/tenant";

function fmt(v: string | number): string {
  try {
    return new Decimal(typeof v === "string" ? v : v.toString()).toFixed(2);
  } catch {
    return String(v);
  }
}

export default function SupplierPaymentPrintPage() {
  const params = useParams<{ id: string }>();
  const searchParams = useSearchParams();
  const forceTwoCopies = searchParams.get("copies") === "2";
  const supplierNames = useSupplierNameMap();
  const bankNames = useBankAccountNameMap();
  const billNumbers = useBillNumberMap();

  const { query, businessName, businessAddress, businessLogoUrl, template, isLoading, error } = useVoucherPrintPage(
    ["print-supplier-payment", params.id],
    () => purchasesApi.getSupplierPayment(params.id),
    !!params.id,
    "vp",
  );

  const pay = query.data?.result;
  const allocations = query.data?.allocations ?? [];

  return (
    <PrintQueryShell
      isLoading={isLoading}
      error={error}
      ready={Boolean(pay)}
      notFoundMessage="Payment not found."
    >
      {pay ? (
        <VoucherPrint
          title="Supplier Payment"
          documentNumber={String(pay.voucherNumber ?? pay.id.slice(0, 8))}
          documentDate={pay.paymentDate}
          businessName={businessName}
          businessAddress={businessAddress}
          businessLogoUrl={businessLogoUrl}
          fields={[
            {
              label: "Supplier",
              value: supplierNames.get(pay.supplierId ?? "") ?? pay.supplierId ?? "—",
            },
            {
              label: "Bank account",
              value: bankNames.get(pay.bankAccountId) ?? pay.bankAccountId,
            },
            { label: "Amount", value: fmt(pay.totalAmount) },
            { label: "Status", value: pay.status ?? "—" },
          ]}
          tableHeaders={["Bill", "Allocated"]}
          tableRows={allocations.map((a) => [
            billNumbers.get(a.supplierBillId ?? "") ?? a.supplierBillId ?? "—",
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
