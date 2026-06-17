/** Sales credits list — catalog §5.5 */
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
import { salesCreditsApi, type SalesCredit } from "@/lib/api/tenant";

export default function SalesCreditsPage() {
  const router = useRouter();
  const customerNames = useCustomerNameMap();
  const { data, isLoading, error } = useTenantListQuery(["sales-credits"], () => salesCreditsApi.list());

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) => matchText([r.creditNumber, customerNames.get(r.customerId)], q),
  });

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<SalesCredit>([
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
          key: "customerId",
          header: "Customer",
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
        { key: "journalId", header: "Posted", render: (r) => (r.journalId ? "Yes" : "—") },
      ]),
    [customerNames],
  );
  const columns = useConfiguredListColumns("sales-credit", baseColumns);

  return (
    <div>
      <PageHeader
        title="Sales credits"
        breadcrumb="Sell / Credits"
        actions={
          <Button asChild>
            <Link href="/sales/credits/new">New credit</Link>
          </Button>
        }
      />
      <ListToolbar search={search} onSearchChange={setSearch} />
      <EnterpriseGrid<SalesCredit>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        listEntity="sales-credit"
        isSearching={Boolean(search)}
        onRowClick={(r) => r.id && router.push(`/sales/credits/${r.id}`)}
        pagination={pagination}
        exportCsv={{ ...buildGridExport("sales-credits", columns), rows: filtered }}
      />
    </div>
  );
}
