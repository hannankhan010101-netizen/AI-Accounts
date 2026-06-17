/** Purchase credits list — catalog §6.5 */
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
import { supplierCreditsApi, type SupplierCredit } from "@/lib/api/tenant";

export default function PurchaseCreditsPage() {
  const router = useRouter();
  const supplierNames = useSupplierNameMap();
  const { data, isLoading, error } = useTenantListQuery(["supplier-credits"], () => supplierCreditsApi.list());

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) => matchText([r.creditNumber, supplierNames.get(r.supplierId)], q),
  });

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<SupplierCredit>([
        {
          key: "creditNumber",
          header: "Credit no.",
          sortable: true,
          sortAccessor: (r) => r.creditNumber,
        },
        {
          key: "creditDate",
          header: "Date",
          sortable: true,
          sortAccessor: (r) => r.creditDate,
          render: (r) => new Date(r.creditDate).toLocaleDateString(),
        },
        {
          key: "supplierId",
          header: "Supplier",
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
  const columns = useConfiguredListColumns("supplier-credit", baseColumns);

  return (
    <div>
      <PageHeader
        title="Purchase credits"
        breadcrumb="Buy / Credits"
        actions={
          <Button asChild>
            <Link href="/purchases/credits/new">New credit</Link>
          </Button>
        }
      />
      <ListToolbar search={search} onSearchChange={setSearch} />
      <EnterpriseGrid<SupplierCredit>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        listEntity="purchase-credit"
        isSearching={Boolean(search)}
        onRowClick={(r) => r.id && router.push(`/purchases/credits/${r.id}`)}
        pagination={pagination}
        exportCsv={{ ...buildGridExport("supplier-credits", columns), rows: filtered }}
      />
    </div>
  );
}
