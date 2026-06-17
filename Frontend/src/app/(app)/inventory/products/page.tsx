/** Products list — catalog §7.1 */
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
import { matchText } from "@/lib/list/document-list-filters";
import { inventoryApi, type Product } from "@/lib/api/tenant";

export default function ProductsPage() {
  const router = useRouter();
  const { data, isLoading, error } = useTenantListQuery(["products"], () => inventoryApi.listProducts());

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) => matchText([r.code, r.name, r.unit], q),
  });

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<Product>([
        { key: "code", header: "Code", sortable: true, sortAccessor: (r) => r.code ?? "" },
        { key: "name", header: "Product", sortable: true, sortAccessor: (r) => r.name },
        { key: "unit", header: "Unit" },
        { key: "salePrice", header: "Sale price", align: "right" },
        { key: "cost", header: "Cost", align: "right" },
      ]),
    [],
  );
  const columns = useConfiguredListColumns("products", baseColumns);

  return (
    <div>
      <PageHeader
        title="Products"
        breadcrumb="Stock / Products"
        tourRoot="inventory-products-header"
        tourActions="inventory-products-new"
        actions={
          <Link href="/inventory/products/new">
            <Button>Add product</Button>
          </Link>
        }
      />
      <ListToolbar search={search} onSearchChange={setSearch} />
      <EnterpriseGrid<Product>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        emptyMessage="No products yet."
        pagination={pagination}
        exportCsv={{ ...buildGridExport("products", columns), rows: filtered }}
        tourTarget="inventory-products-grid"
        onRowClick={(r) => router.push(`/inventory/products/${r.id}`)}
      />
    </div>
  );
}
