/** Stock transfer list — catalog §7.2 */
"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useMemo } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { buildGridExport } from "@/lib/export/grid-export";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { PageHeader } from "@/components/ui/page-header";
import { useClientList } from "@/lib/hooks/use-client-list";
import { useConfiguredListColumns } from "@/lib/hooks/use-configured-list-columns";
import { matchText } from "@/lib/list/document-list-filters";
import { inventoryWritesApi, type StockTransfer } from "@/lib/api/tenant";

export default function StockTransferPage() {
  const router = useRouter();
  const { data, isLoading, error } = useTenantListQuery(["stock-transfers"], () => inventoryWritesApi.listStockTransfers());

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) => matchText([r.voucherNumber, r.fromLocationCode, r.toLocationCode], q),
  });

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<StockTransfer>([
        {
          key: "voucherNumber",
          header: "Voucher",
          render: (r) => (
            <Link href={`/inventory/stock-transfer/${r.id}`} className="font-mono text-brand hover:underline">
              {r.voucherNumber}
            </Link>
          ),
        },
        {
          key: "transferDate",
          header: "Date",
          render: (r) => new Date(r.transferDate).toLocaleDateString(),
        },
        { key: "fromLocationCode", header: "From" },
        { key: "toLocationCode", header: "To" },
        {
          key: "lineCount",
          header: "Lines",
          align: "right",
          render: (r) => r.lines?.length ?? 0,
        },
      ]),
    [],
  );
  const columns = useConfiguredListColumns("stock-transfer", baseColumns);

  return (
    <div>
      <PageHeader
        title="Stock transfer"
        breadcrumb="Stock / Stock transfer"
        actions={
          <Link href="/inventory/stock-transfer/new">
            <Button>New transfer</Button>
          </Link>
        }
      />
      <ListToolbar search={search} onSearchChange={setSearch} />
      <EnterpriseGrid<StockTransfer>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        emptyMessage="No stock transfers yet."
        onRowClick={(r) => router.push(`/inventory/stock-transfer/${r.id}`)}
        pagination={pagination}
        exportCsv={{ ...buildGridExport("stock-transfers", columns), rows: filtered }}
      />
    </div>
  );
}
