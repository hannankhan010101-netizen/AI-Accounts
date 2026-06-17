/** Stock adjustment list — catalog §7.3 */
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
import { inventoryWritesApi, type StockAdjustment } from "@/lib/api/tenant";

export default function StockAdjustmentPage() {
  const router = useRouter();
  const { data, isLoading, error } = useTenantListQuery(["stock-adjustments"], () => inventoryWritesApi.listStockAdjustments());

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) => matchText([r.voucherNumber, r.reason, r.status], q),
  });

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<StockAdjustment>([
        {
          key: "voucherNumber",
          header: "Voucher",
          render: (r) => (
            <Link
              href={`/inventory/stock-adjustment/${r.id}`}
              className="font-mono text-brand hover:underline"
            >
              {r.voucherNumber}
            </Link>
          ),
        },
        {
          key: "adjustmentDate",
          header: "Date",
          render: (r) => new Date(r.adjustmentDate).toLocaleDateString(),
        },
        { key: "reason", header: "Reason" },
        { key: "status", header: "Status" },
        {
          key: "lineCount",
          header: "Lines",
          align: "right",
          render: (r) => r.lines?.length ?? 0,
        },
      ]),
    [],
  );
  const columns = useConfiguredListColumns("stock-adjustment", baseColumns);

  return (
    <div>
      <PageHeader
        title="Stock adjustment"
        breadcrumb="Stock / Stock adjustment"
        actions={
          <Link href="/inventory/stock-adjustment/new">
            <Button>New adjustment</Button>
          </Link>
        }
      />
      <ListToolbar search={search} onSearchChange={setSearch} />
      <EnterpriseGrid<StockAdjustment>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        emptyMessage="No stock adjustments yet."
        onRowClick={(r) => router.push(`/inventory/stock-adjustment/${r.id}`)}
        pagination={pagination}
        exportCsv={{ ...buildGridExport("stock-adjustments", columns), rows: filtered }}
      />
    </div>
  );
}
