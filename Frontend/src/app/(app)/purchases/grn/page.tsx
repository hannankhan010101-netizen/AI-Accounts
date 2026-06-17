/** Goods receipt notes — catalog §6 */
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
import { useSupplierNameMap } from "@/lib/hooks/use-party-name-map";
import { matchText } from "@/lib/list/document-list-filters";
import { deliveryApi, type GoodsReceiptNote } from "@/lib/api/tenant";

export default function GrnPage() {
  const router = useRouter();
  const supplierNames = useSupplierNameMap();
  const { data, isLoading, error } = useTenantListQuery(["grns"], () => deliveryApi.listGrns());

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) =>
      matchText([r.voucherNumber, supplierNames.get(r.supplierId), r.sourceKind, r.status], q),
  });

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<GoodsReceiptNote>([
        {
          key: "voucherNumber",
          header: "Voucher",
          sortable: true,
          sortAccessor: (r) => r.voucherNumber,
        },
        {
          key: "receiptDate",
          header: "Date",
          sortable: true,
          sortAccessor: (r) => r.receiptDate,
          render: (r) => new Date(r.receiptDate).toLocaleDateString(),
        },
        {
          key: "supplierId",
          header: "Supplier",
          render: (r) => supplierNames.get(r.supplierId) ?? r.supplierId,
        },
        { key: "sourceKind", header: "Source" },
        { key: "status", header: "Status" },
      ]),
    [supplierNames],
  );
  const columns = useConfiguredListColumns("grn", baseColumns);

  return (
    <div>
      <PageHeader
        title="Goods received"
        breadcrumb="Buy / Goods received"
        actions={
          <Button asChild>
            <Link href="/purchases/grn/new">New GRN</Link>
          </Button>
        }
      />
      <ListToolbar search={search} onSearchChange={setSearch} />
      <EnterpriseGrid<GoodsReceiptNote>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        listEntity="purchase-grn"
        isSearching={Boolean(search)}
        onRowClick={(r) => r.id && router.push(`/purchases/grn/${r.id}`)}
        pagination={pagination}
        exportCsv={{ ...buildGridExport("grn", columns), rows: filtered }}
      />
    </div>
  );
}
