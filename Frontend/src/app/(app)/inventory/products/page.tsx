/** Products list — catalog §7.1 */
"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useMemo } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";

import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { useConfiguredListColumns } from "@/lib/hooks/use-configured-list-columns";
import { buildGridExport } from "@/lib/export/grid-export";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { PageHeader } from "@/components/ui/page-header";
import { attachmentsApi, inventoryApi, type Product } from "@/lib/api/tenant";
import {
  listSearchHref,
  parseListPage,
  parseListQuery,
  patchListSearchParams,
} from "@/lib/navigation/list-search-params";

const PAGE_SIZE = 25;

export default function ProductsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const page = parseListPage(searchParams);
  const search = parseListQuery(searchParams);
  const trimmedSearch = search.trim();

  const { data, isLoading, error } = useTenantListQuery(
    ["products", page, trimmedSearch],
    () =>
      trimmedSearch
        ? inventoryApi.searchProducts(trimmedSearch, 100)
        : inventoryApi.listProducts({ page, pageSize: PAGE_SIZE }),
  );

  const rows = data?.result ?? [];
  const total = trimmedSearch ? rows.length : (data?.total ?? rows.length);
  const pageCount = trimmedSearch ? 1 : Math.max(1, Math.ceil(total / PAGE_SIZE));

  const pagination = {
    page: trimmedSearch ? 1 : page,
    pageCount,
    total,
    pageSize: trimmedSearch ? total || PAGE_SIZE : PAGE_SIZE,
    onPageChange: (next: number) => {
      const params = patchListSearchParams(searchParams, { page: next });
      router.push(listSearchHref("/inventory/products", params));
    },
  };

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<Product>([
        {
          key: "primaryImageAttachmentId",
          header: "",
          width: 48,
          render: (r) =>
            r.primaryImageAttachmentId ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={attachmentsApi.productImageUrl(r.primaryImageAttachmentId) ?? ""}
                alt=""
                className="h-8 w-8 rounded object-cover"
              />
            ) : (
              <span className="inline-block h-8 w-8 rounded bg-canvas" />
            ),
        },
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
          <Link href="/inventory/add">
            <Button>Add product</Button>
          </Link>
        }
      />
      <ListToolbar
        search={search}
        onSearchChange={(q) => {
          const params = patchListSearchParams(searchParams, { q });
          router.push(listSearchHref("/inventory/products", params));
        }}
      />
      <EnterpriseGrid<Product>
        columns={columns}
        rows={rows}
        loading={isLoading}
        error={error}
        emptyMessage="No products yet."
        pagination={pagination}
        exportCsv={{ ...buildGridExport("products", columns), rows }}
        tourTarget="inventory-products-grid"
        onRowClick={(r) => router.push(`/inventory/products/${r.id}`)}
      />
    </div>
  );
}
