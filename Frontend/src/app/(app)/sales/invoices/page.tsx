/** Sales Invoices list — catalog §5.4 */
"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useMemo } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { buildGridExport } from "@/lib/export/grid-export";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { PageHeader } from "@/components/ui/page-header";
import { useClientList } from "@/lib/hooks/use-client-list";
import { useCustomerNameMap } from "@/lib/hooks/use-party-name-map";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { useConfiguredListColumns } from "@/lib/hooks/use-configured-list-columns";
import { matchText } from "@/lib/list/document-list-filters";
import { salesApi, type SalesInvoice } from "@/lib/api/tenant";

export default function SalesInvoicesPage() {
  const router = useRouter();
  const customerNameById = useCustomerNameMap();

  const { data, isLoading, error } = useTenantListQuery(["sales-invoices"], () => salesApi.listInvoices());

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) =>
      matchText(
        [r.documentNumber as string, customerNameById.get(r.customerId), r.customerId],
        q,
      ),
  });

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<SalesInvoice>([
        {
          key: "documentNumber",
          header: "Doc no.",
          sortable: true,
          sortAccessor: (r) => String(r.documentNumber ?? r.id),
          render: (r) => (
            <Link href={`/sales/invoices/${r.id}`} className="font-mono text-brand hover:underline">
              {r.documentNumber ?? r.id.slice(0, 8)}
            </Link>
          ),
        },
        {
          key: "invoiceDate",
          header: "Date",
          sortable: true,
          sortAccessor: (r) => r.invoiceDate,
          render: (r) => new Date(r.invoiceDate).toLocaleDateString(),
        },
        {
          key: "customerId",
          header: "Customer",
          sortable: true,
          sortAccessor: (r) => customerNameById.get(r.customerId) ?? r.customerId,
          render: (r) => customerNameById.get(r.customerId) ?? r.customerId,
        },
        {
          key: "totalAmount",
          header: "Total",
          align: "right",
          sortable: true,
          sortAccessor: (r) => Number(r.totalAmount),
        },
      ]),
    [customerNameById],
  );
  const columns = useConfiguredListColumns("sales-invoice", baseColumns);

  return (
    <div>
      <PageHeader
        title="Sales invoices"
        breadcrumb="Sell / Invoices"
        tourRoot="sales-invoices-header"
        tourActions="sales-invoices-new"
        actions={
          <>
            <Button asChild variant="outline">
              <Link href="/sales/all">All sales activity</Link>
            </Button>
            <Button asChild>
              <Link href="/sales/invoices/new">New invoice</Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/sales/invoices/batch">Batch entry</Link>
            </Button>
          </>
        }
      />
      <ListToolbar
        search={search}
        onSearchChange={setSearch}
        searchPlaceholder="Search doc no. or customer…"
      />
      <EnterpriseGrid<SalesInvoice>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        listEntity="sales-invoice"
        isSearching={Boolean(search)}
        onRowClick={(row) => router.push(`/sales/invoices/${row.id}`)}
        pagination={pagination}
        exportCsv={{ ...buildGridExport("sales-invoices", columns), rows: filtered }}
        tourTarget="sales-invoices-grid"
      />
    </div>
  );
}
