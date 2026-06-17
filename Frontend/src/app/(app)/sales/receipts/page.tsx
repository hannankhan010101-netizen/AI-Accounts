/** Sales receipts list — catalog §5.8 */
"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useMemo } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { useConfiguredListColumns } from "@/lib/hooks/use-configured-list-columns";
import { buildGridExport } from "@/lib/export/grid-export";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { PageHeader } from "@/components/ui/page-header";
import { useClientList } from "@/lib/hooks/use-client-list";
import { useBankAccountNameMap } from "@/lib/hooks/use-bank-account-name-map";
import { useCustomerNameMap } from "@/lib/hooks/use-party-name-map";
import { matchText } from "@/lib/list/document-list-filters";
import { salesApi, type SalesReceipt } from "@/lib/api/tenant";

export default function SalesReceiptsPage() {
  const router = useRouter();
  const customerNames = useCustomerNameMap();
  const bankNames = useBankAccountNameMap();
  const { data, isLoading, error } = useTenantListQuery(["sales-receipts"], () => salesApi.listReceipts());

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) =>
      matchText([r.receiptNumber as string, customerNames.get(r.customerId)], q),
  });

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<SalesReceipt>([
        {
          key: "receiptNumber",
          header: "Voucher",
          render: (r) => (
            <Link href={`/sales/receipts/${r.id}`} className="text-brand hover:underline">
              {r.receiptNumber ?? r.id.slice(0, 8)}
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
          key: "customerId",
          header: "Customer",
          render: (r) => customerNames.get(r.customerId) ?? r.customerId,
        },
        {
          key: "bankAccountId",
          header: "Bank",
          render: (r) => bankNames.get(r.bankAccountId) ?? r.bankAccountId,
        },
        {
          key: "totalAmount",
          header: "Amount",
          align: "right",
          sortable: true,
          sortAccessor: (r) => Number(r.totalAmount),
        },
        {
          key: "unallocatedBalance",
          header: "Balance",
          align: "right",
          sortable: true,
          sortAccessor: (r) => Number(r.unallocatedBalance ?? 0),
          render: (r) => {
            const bal = r.unallocatedBalance;
            if (bal == null || bal === "") return "—";
            const n = Number(bal);
            return n > 0.009 ? n.toFixed(2) : "—";
          },
        },
        {
          key: "return",
          header: "",
          render: (r) => {
            const n = Number(r.unallocatedBalance ?? 0);
            if (n <= 0.009) return null;
            return (
              <Link
                href={`/sales/receipts/${r.id}/return-advance`}
                className="text-brand hover:underline"
                onClick={(e) => e.stopPropagation()}
              >
                Return
              </Link>
            );
          },
        },
        {
          key: "journalId",
          header: "Posted",
          render: (r) => (r.journalId ? "Yes" : "—"),
        },
      ]),
    [customerNames, bankNames],
  );
  const columns = useConfiguredListColumns("sales-receipt", baseColumns);

  return (
    <div>
      <PageHeader
        title="Sales receipts"
        breadcrumb="Sell / Receipts"
        tourRoot="sales-receipts-header"
        tourActions="sales-receipts-new"
        actions={
          <Button asChild>
            <Link href="/sales/receipts/new">New receipt</Link>
          </Button>
        }
      />
      <ListToolbar search={search} onSearchChange={setSearch} searchPlaceholder="Search receipts…" />
      <EnterpriseGrid<SalesReceipt>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        listEntity="sales-receipt"
        isSearching={Boolean(search)}
        onRowClick={(r) => router.push(`/sales/receipts/${r.id}`)}
        pagination={pagination}
        exportCsv={{ ...buildGridExport("sales-receipts", columns), rows: filtered }}
      />
    </div>
  );
}
