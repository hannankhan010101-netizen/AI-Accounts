/** Sales orders list — catalog §5.3 */
"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useMemo } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { StatusBadge } from "@/components/app/status-badge";
import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { useConfiguredListColumns } from "@/lib/hooks/use-configured-list-columns";
import { buildGridExport } from "@/lib/export/grid-export";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { PageHeader } from "@/components/ui/page-header";
import { useClientList } from "@/lib/hooks/use-client-list";
import { useCustomerNameMap } from "@/lib/hooks/use-party-name-map";
import { matchText } from "@/lib/list/document-list-filters";
import { salesOrdersApi, type SalesOrder } from "@/lib/api/tenant";

export default function SalesOrdersPage() {
  const router = useRouter();
  const customerNames = useCustomerNameMap();
  const { data, isLoading, error } = useTenantListQuery(["sales-orders"], () => salesOrdersApi.list());

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) =>
      matchText([r.orderNumber, customerNames.get(r.customerId), r.status], q),
  });

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<SalesOrder>([
    {
      key: "orderNumber",
      header: "Order no.",
      sortable: true,
      sortAccessor: (r) => r.orderNumber,
      render: (r) => (
        <Link href={`/sales/orders/${r.id}`} className="font-mono text-brand hover:underline">
          {r.orderNumber}
        </Link>
      ),
    },
    {
      key: "orderDate",
      header: "Date",
      sortable: true,
      sortAccessor: (r) => r.orderDate,
      render: (r) => new Date(r.orderDate).toLocaleDateString(),
    },
    {
      key: "customerId",
      header: "Customer",
      sortable: true,
      sortAccessor: (r) => customerNames.get(r.customerId) ?? r.customerId,
      render: (r) => customerNames.get(r.customerId) ?? r.customerId,
    },
    { key: "status", header: "Status", render: (r) => <StatusBadge status={r.status} /> },
    { key: "totalAmount", header: "Total", align: "right", sortable: true, sortAccessor: (r) => Number(r.totalAmount) },
      ]),
    [],
  );
  const columns = useConfiguredListColumns("sales-order", baseColumns);

  return (
    <div>
      <PageHeader
        title="Sales orders"
        breadcrumb="Sell / Orders"
        actions={
          <Button asChild>
            <Link href="/sales/orders/new">New order</Link>
          </Button>
        }
      />
      <ListToolbar search={search} onSearchChange={setSearch} searchPlaceholder="Search orders…" />
      <EnterpriseGrid<SalesOrder>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        listEntity="sales-order"
        isSearching={Boolean(search)}
        onRowClick={(r) => router.push(`/sales/orders/${r.id}`)}
        pagination={pagination}
        exportCsv={{ ...buildGridExport("sales-orders", columns), rows: filtered }}
      />
    </div>
  );
}
