/** Post-Dated Cheques Received — catalog §5.7. */
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
import { useCustomerNameMap } from "@/lib/hooks/use-party-name-map";
import { useClientList } from "@/lib/hooks/use-client-list";
import { matchText } from "@/lib/list/document-list-filters";
import { pdcApi, type PdcReceived } from "@/lib/api/tenant";

export default function PdcReceivedPage() {
  const router = useRouter();
  const customerNames = useCustomerNameMap();
  const { data, isLoading, error } = useTenantListQuery(["pdc-received"], () => pdcApi.listReceived());

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) =>
      matchText([r.voucherNumber, r.chequeNumber, r.bankName, r.customerId, r.status], q),
  });

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<PdcReceived>([
        { key: "voucherNumber", header: "V. No." },
        { key: "chequeNumber", header: "Cheque" },
        { key: "bankName", header: "Bank" },
        {
          key: "customerId",
          header: "Customer",
          render: (r) => customerNames.get(r.customerId) ?? r.customerId,
        },
        {
          key: "chequeDate",
          header: "Cheque date",
          render: (r) => new Date(r.chequeDate).toLocaleDateString(),
        },
        { key: "amount", header: "Amount", align: "right" },
        {
          key: "status",
          header: "Status",
          render: (r) => <StatusBadge status={r.status} />,
        },
      ]),
    [customerNames],
  );

  const columns = useConfiguredListColumns("pdc-received", baseColumns);

  return (
    <div>
      <PageHeader
        title="Post Dated Cheque Received"
        breadcrumb="Home / Sales / PDC Received"
        description="Track customer post-dated cheques through pending → presented → cleared / bounced (§5.7)."
        actions={
          <Button asChild>
            <Link href="/sales/pdc-received/new">+ New PDC</Link>
          </Button>
        }
      />
      <ListToolbar search={search} onSearchChange={setSearch} />
      <EnterpriseGrid<PdcReceived>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        listEntity="sales-pdc-received"
        isSearching={Boolean(search)}
        pagination={pagination}
        exportCsv={{ ...buildGridExport("pdc-received", columns), rows: filtered }}
        getRowId={(r) => r.id}
        onRowClick={(r) => router.push(`/sales/pdc-received/${r.id}`)}
      />
    </div>
  );
}
