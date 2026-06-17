/** Bank payments list — catalog §4.2 */
"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useMemo } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { EnterpriseGrid } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { useConfiguredListColumns } from "@/lib/hooks/use-configured-list-columns";
import { buildGridExport } from "@/lib/export/grid-export";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { PageHeader } from "@/components/ui/page-header";
import { useClientList } from "@/lib/hooks/use-client-list";
import { useBankAccountNameMap } from "@/lib/hooks/use-bank-account-name-map";
import { matchText } from "@/lib/list/document-list-filters";
import { bankApi, type BankPayment } from "@/lib/api/tenant";

export default function BankPaymentsPage() {
  const router = useRouter();
  const bankNames = useBankAccountNameMap();
  const { data, isLoading, error } = useTenantListQuery(["bank-payments"], () => bankApi.listPayments());

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) =>
      matchText([r.voucherNumber as string, bankNames.get(r.bankAccountId), r.bankAccountId], q),
  });

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<BankPayment>([
        {
          key: "voucherNumber",
          header: "Voucher",
          render: (r) => (
            <Link href={`/bank/payments/${r.id}`} className="font-medium text-brand hover:underline">
              {r.voucherNumber ?? r.id.slice(0, 8)}
            </Link>
          ),
        },
        {
          key: "paymentDate",
          header: "Date",
          sortable: true,
          sortAccessor: (r) => r.paymentDate,
          render: (r) => new Date(r.paymentDate).toLocaleDateString(),
        },
        {
          key: "bankAccountId",
          header: "Bank account",
          render: (r) => bankNames.get(r.bankAccountId) ?? r.bankAccountId,
        },
        {
          key: "totalAmount",
          header: "Amount",
          align: "right",
          sortable: true,
          sortAccessor: (r) => Number(r.totalAmount),
        },
      ]),
    [bankNames],
  );

  const columns = useConfiguredListColumns("bank-payments", baseColumns);

  return (
    <div>
      <PageHeader
        title="Bank payments"
        breadcrumb="Money / Payments out"
        tourRoot="bank-payments-header"
        tourActions="bank-payments-new"
        actions={
          <Link href="/bank/payments/new">
            <Button>New payment</Button>
          </Link>
        }
      />
      <ListToolbar search={search} onSearchChange={setSearch} />
      <EnterpriseGrid<BankPayment>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        listEntity="bank-payment"
        isSearching={Boolean(search)}
        onRowClick={(r) => router.push(`/bank/payments/${r.id}`)}
        pagination={pagination}
        exportCsv={{ ...buildGridExport("bank-payments", columns), rows: filtered }}
      />
    </div>
  );
}
