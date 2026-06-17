"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import Decimal from "decimal.js";

import { PrintQueryShell } from "@/components/print/print-query-shell";
import { VoucherPrint } from "@/components/print/voucher-print";
import { useBankAccountNameMap } from "@/lib/hooks/use-bank-account-name-map";
import { useSupplierNameMap } from "@/lib/hooks/use-party-name-map";
import { useVoucherPrintPage } from "@/lib/hooks/use-voucher-print-page";
import { bankApi, pdcApi } from "@/lib/api/tenant";

function fmt(v: string | number): string {
  try {
    return new Decimal(typeof v === "string" ? v : v.toString()).toFixed(2);
  } catch {
    return String(v);
  }
}

export default function PdcIssuedPrintPage() {
  const params = useParams<{ id: string }>();
  const supplierNames = useSupplierNameMap();
  const bankNames = useBankAccountNameMap();

  const { data: banks, isLoading: banksLoading } = useTenantListQuery(["bank-accounts"], () => bankApi.listAccounts());

  const { query, businessName, businessAddress, businessLogoUrl, template, isLoading, error } = useVoucherPrintPage(
    ["print-pdc-issued", params.id],
    () => pdcApi.getIssued(params.id),
    !!params.id,
  
    "pdci",
  );

  const row = query.data?.result;
  const bankLabel = row
    ? (banks?.result.find((b) => b.id === row.bankAccountId)?.name ??
      bankNames.get(row.bankAccountId) ??
      row.bankAccountId)
    : "";

  return (
    <PrintQueryShell
      isLoading={isLoading || banksLoading}
      error={error}
      ready={Boolean(row)}
      notFoundMessage="Cheque not found."
    >
      {row ? (
        <VoucherPrint
          title="PDC Issued"
          documentNumber={row.voucherNumber}
          documentDate={row.issuedDate}
          businessName={businessName}
          businessAddress={businessAddress}
          businessLogoUrl={businessLogoUrl}
          template={template}
          fields={[
            { label: "Cheque no.", value: row.chequeNumber },
            { label: "Amount", value: fmt(row.amount) },
            {
              label: "Supplier",
              value: supplierNames.get(row.supplierId) ?? row.supplierId,
            },
            { label: "Bank account", value: bankLabel },
            {
              label: "Cheque date",
              value: new Date(row.chequeDate).toLocaleDateString(),
            },
            { label: "Status", value: row.status },
          ]}
        />
      ) : null}
    </PrintQueryShell>
  );
}
