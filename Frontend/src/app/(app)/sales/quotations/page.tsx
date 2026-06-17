/** Quotations list — catalog §5.2 */
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
import { useCustomerNameMap } from "@/lib/hooks/use-party-name-map";
import { matchText } from "@/lib/list/document-list-filters";
import { quotationsApi, type Quotation } from "@/lib/api/tenant";

export default function QuotationsPage() {
  const router = useRouter();
  const customerNames = useCustomerNameMap();
  const { data, isLoading, error } = useTenantListQuery(["quotations"], () => quotationsApi.list());

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) =>
      matchText([r.quotationNumber, customerNames.get(r.customerId), r.status], q),
  });

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<Quotation>([
        {
          key: "quotationNumber",
          header: "Quote no.",
          sortable: true,
          sortAccessor: (r) => r.quotationNumber,
          render: (r) => (
            <Link href={`/sales/quotations/${r.id}`} className="font-mono text-brand hover:underline">
              {r.quotationNumber}
            </Link>
          ),
        },
        {
          key: "quotationDate",
          header: "Date",
          sortable: true,
          sortAccessor: (r) => r.quotationDate,
          render: (r) => new Date(r.quotationDate).toLocaleDateString(),
        },
        {
          key: "customerId",
          header: "Customer",
          sortable: true,
          sortAccessor: (r) => customerNames.get(r.customerId) ?? r.customerId,
          render: (r) => customerNames.get(r.customerId) ?? r.customerId,
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
    [customerNames],
  );
  const columns = useConfiguredListColumns("quotation", baseColumns);

  return (
    <div>
      <PageHeader
        title="Quotations"
        breadcrumb="Sell / Quotations"
        actions={
          <Button asChild>
            <Link href="/sales/quotations/new">New quotation</Link>
          </Button>
        }
      />
      <ListToolbar search={search} onSearchChange={setSearch} searchPlaceholder="Search quotations…" />
      <EnterpriseGrid<Quotation>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        listEntity="sales-quotation"
        isSearching={Boolean(search)}
        onRowClick={(r) => router.push(`/sales/quotations/${r.id}`)}
        pagination={pagination}
        exportCsv={{ ...buildGridExport("quotations", columns), rows: filtered }}
      />
    </div>
  );
}
