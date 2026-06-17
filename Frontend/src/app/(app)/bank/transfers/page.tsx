/** Bank transfers list — catalog §4.4 */
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
import { bankApi, type BankTransfer } from "@/lib/api/tenant";

export default function BankTransfersPage() {
  const router = useRouter();
  const bankNames = useBankAccountNameMap();
  const { data, isLoading, error } = useTenantListQuery(["bank-transfers"], () => bankApi.listTransfers());

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) =>
      matchText(
        [
          r.voucherNumber as string,
          bankNames.get(r.fromBankAccountId),
          bankNames.get(r.toBankAccountId),
        ],
        q,
      ),
  });

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<BankTransfer>([
        {
          key: "voucherNumber",
          header: "Transfer",
          sortable: true,
          sortAccessor: (r) => r.voucherNumber ?? r.id,
          render: (r) => (
            <Link href={`/bank/transfers/${r.id}`} className="font-medium text-brand hover:underline">
              {r.voucherNumber ?? r.id.slice(0, 8)}
            </Link>
          ),
        },
        {
          key: "transferDate",
          header: "Date",
          sortable: true,
          sortAccessor: (r) => r.transferDate,
          render: (r) => new Date(r.transferDate).toLocaleDateString(),
        },
        {
          key: "fromBankAccountId",
          header: "From",
          render: (r) => bankNames.get(r.fromBankAccountId) ?? r.fromBankAccountId,
        },
        {
          key: "toBankAccountId",
          header: "To",
          render: (r) => bankNames.get(r.toBankAccountId) ?? r.toBankAccountId,
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
  const columns = useConfiguredListColumns("bank-transfer", baseColumns);

  return (
    <div>
      <PageHeader
        title="Bank transfers"
        breadcrumb="Money / Transfers"
        actions={
          <Link href="/bank/transfers/new">
            <Button>New transfer</Button>
          </Link>
        }
      />
      <ListToolbar search={search} onSearchChange={setSearch} />
      <EnterpriseGrid<BankTransfer>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        listEntity="bank-transfer"
        isSearching={Boolean(search)}
        onRowClick={(r) => router.push(`/bank/transfers/${r.id}`)}
        pagination={pagination}
        exportCsv={{ ...buildGridExport("bank-transfers", columns), rows: filtered }}
      />
    </div>
  );
}
