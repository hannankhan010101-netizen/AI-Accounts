/** Purchase orders list — catalog §6.2 */
"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useMemo } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { StatusBadge } from "@/components/app/status-badge";
import { Button } from "@/components/ui/button";
import { EnterpriseGrid } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { useConfiguredListColumns } from "@/lib/hooks/use-configured-list-columns";
import { buildGridExport } from "@/lib/export/grid-export";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { PageHeader } from "@/components/ui/page-header";
import { useClientList } from "@/lib/hooks/use-client-list";
import { useSupplierNameMap } from "@/lib/hooks/use-party-name-map";
import { matchText } from "@/lib/list/document-list-filters";
import { purchaseOrdersApi, type PurchaseOrder } from "@/lib/api/tenant";

export default function PurchaseOrdersPage() {
  const router = useRouter();
  const supplierNames = useSupplierNameMap();
  const { data, isLoading, error } = useTenantListQuery(["purchase-orders"], () => purchaseOrdersApi.list());

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) => matchText([r.orderNumber, supplierNames.get(r.supplierId), r.status], q),
  });

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<PurchaseOrder>([
        {
          key: "orderNumber",
          header: "PO no.",
          sortable: true,
          sortAccessor: (r) => r.orderNumber,
          render: (r) => (
            <Link href={`/purchases/orders/${r.id}`} className="font-mono text-brand hover:underline">
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
          key: "supplierId",
          header: "Supplier",
          sortable: true,
          sortAccessor: (r) => supplierNames.get(r.supplierId) ?? r.supplierId,
          render: (r) => supplierNames.get(r.supplierId) ?? r.supplierId,
        },
        { key: "status", header: "Status", render: (r) => <StatusBadge status={r.status} /> },
        {
          key: "totalAmount",
          header: "Total",
          align: "right",
          sortable: true,
          sortAccessor: (r) => Number(r.totalAmount),
        },
      ]),
    [supplierNames],
  );
  const columns = useConfiguredListColumns("purchase-order", baseColumns);

  return (
    <div>
      <PageHeader
        title="Purchase orders"
        breadcrumb="Buy / Purchase orders"
        actions={
          <Button asChild>
            <Link href="/purchases/orders/new">New PO</Link>
          </Button>
        }
      />
      <ListToolbar search={search} onSearchChange={setSearch} />
      <EnterpriseGrid<PurchaseOrder>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        listEntity="purchase-order"
        isSearching={Boolean(search)}
        onRowClick={(r) => router.push(`/purchases/orders/${r.id}`)}
        pagination={pagination}
        exportCsv={{ ...buildGridExport("purchase-orders", columns), rows: filtered }}
      />
    </div>
  );
}
