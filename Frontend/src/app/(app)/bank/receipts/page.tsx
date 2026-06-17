/** Bank receipts list — catalog §4.3 */
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
import { bankApi, type BankReceipt } from "@/lib/api/tenant";

export default function BankReceiptsPage() {
  const router = useRouter();
  const bankNames = useBankAccountNameMap();
  const { data, isLoading, error } = useTenantListQuery(["bank-receipts"], () => bankApi.listReceipts());

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) =>
      matchText([r.voucherNumber as string, bankNames.get(r.bankAccountId), r.bankAccountId], q),
  });

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<BankReceipt>([
        {
          key: "voucherNumber",
          header: "Voucher",
          render: (r) => (
            <Link href={`/bank/receipts/${r.id}`} className="font-medium text-brand hover:underline">
              {r.voucherNumber ?? r.id.slice(0, 8)}
            </Link>
          ),
        },
        {
          key: "receiptDate",
          header: "Date",
          sortable: true,
          sortAccessor: (r) => r.receiptDate,
          render: (r) => new Date(r.receiptDate).toLocaleDateString(),
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

  const columns = useConfiguredListColumns("bank-receipts", baseColumns);

  return (
    <div>
      <PageHeader
        title="Bank receipts"
        breadcrumb="Money / Receipts in"
        tourRoot="bank-receipts-header"
        tourActions="bank-receipts-new"
        actions={
          <Link href="/bank/receipts/new">
            <Button>New receipt</Button>
          </Link>
        }
      />
      <ListToolbar search={search} onSearchChange={setSearch} />
      <EnterpriseGrid<BankReceipt>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        listEntity="bank-receipt"
        isSearching={Boolean(search)}
        onRowClick={(r) => router.push(`/bank/receipts/${r.id}`)}
        pagination={pagination}
        exportCsv={{ ...buildGridExport("bank-receipts", columns), rows: filtered }}
      />
    </div>
  );
}
