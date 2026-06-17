/** Supplier bills list — catalog §6.3 */
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
import { useSupplierNameMap } from "@/lib/hooks/use-party-name-map";
import { matchText } from "@/lib/list/document-list-filters";
import { purchasesApi, type SupplierBill } from "@/lib/api/tenant";

export default function SupplierBillsPage() {
  const router = useRouter();
  const supplierNameById = useSupplierNameMap();

  const { data, isLoading, error } = useTenantListQuery(["supplier-bills"], () => purchasesApi.listSupplierBills());

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) =>
      matchText(
        [r.documentNumber as string, supplierNameById.get(r.supplierId), r.supplierId],
        q,
      ),
  });

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<SupplierBill>([
        {
          key: "documentNumber",
          header: "Doc no.",
          sortable: true,
          sortAccessor: (r) => String(r.documentNumber ?? r.id),
          render: (r) => (
            <Link href={`/purchases/bills/${r.id}`} className="font-mono text-brand hover:underline">
              {r.documentNumber ?? r.id.slice(0, 8)}
            </Link>
          ),
        },
        {
          key: "billDate",
          header: "Date",
          sortable: true,
          sortAccessor: (r) => r.billDate,
          render: (r) => new Date(r.billDate).toLocaleDateString(),
        },
        {
          key: "supplierId",
          header: "Supplier",
          sortable: true,
          sortAccessor: (r) => supplierNameById.get(r.supplierId) ?? r.supplierId,
          render: (r) => supplierNameById.get(r.supplierId) ?? r.supplierId,
        },
        {
          key: "totalAmount",
          header: "Total",
          align: "right",
          sortable: true,
          sortAccessor: (r) => Number(r.totalAmount),
        },
      ]),
    [supplierNameById],
  );
  const columns = useConfiguredListColumns("supplier-bill", baseColumns);

  return (
    <div>
      <PageHeader
        title="Supplier bills"
        breadcrumb="Buy / Bills"
        tourRoot="purchase-bills-header"
        tourActions="purchase-bills-new"
        actions={
          <>
            <Button asChild variant="outline">
              <Link href="/purchases/all">All purchase activity</Link>
            </Button>
            <Button asChild>
              <Link href="/purchases/bills/new">New bill</Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/purchases/bills/batch">Batch entry</Link>
            </Button>
          </>
        }
      />
      <ListToolbar search={search} onSearchChange={setSearch} searchPlaceholder="Search doc no. or supplier…" />
      <EnterpriseGrid<SupplierBill>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        listEntity="purchase-bill"
        isSearching={Boolean(search)}
        onRowClick={(row) => router.push(`/purchases/bills/${row.id}`)}
        pagination={pagination}
        exportCsv={{ ...buildGridExport("supplier-bills", columns), rows: filtered }}
      />
    </div>
  );
}
