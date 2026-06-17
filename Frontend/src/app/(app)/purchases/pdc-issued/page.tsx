/** Post-Dated Cheques — catalog §6.1. */
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
import { useBankAccountNameMap } from "@/lib/hooks/use-bank-account-name-map";
import { useSupplierNameMap } from "@/lib/hooks/use-party-name-map";
import { useClientList } from "@/lib/hooks/use-client-list";
import { matchText } from "@/lib/list/document-list-filters";
import { pdcApi, type PdcIssued } from "@/lib/api/tenant";

export default function PdcIssuedPage() {
  const router = useRouter();
  const supplierNames = useSupplierNameMap();
  const bankNames = useBankAccountNameMap();
  const { data, isLoading, error } = useTenantListQuery(["pdc-issued"], () => pdcApi.listIssued());

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) =>
      matchText([r.voucherNumber, r.chequeNumber, r.bankAccountId, r.supplierId, r.status], q),
  });

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<PdcIssued>([
        { key: "voucherNumber", header: "V. No." },
        { key: "chequeNumber", header: "Cheque" },
        {
          key: "bankAccountId",
          header: "From bank",
          render: (r) => bankNames.get(r.bankAccountId) ?? r.bankAccountId,
        },
        {
          key: "supplierId",
          header: "Supplier",
          render: (r) => supplierNames.get(r.supplierId) ?? r.supplierId,
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
    [bankNames, supplierNames],
  );

  const columns = useConfiguredListColumns("pdc-issued", baseColumns);

  return (
    <div>
      <PageHeader
        title="Post Dated Cheque Issued"
        breadcrumb="Home / Purchases / PDC Issued"
        description="Track supplier post-dated cheques through pending → presented → cleared / bounced (§6.1)."
        actions={
          <Button asChild>
            <Link href="/purchases/pdc-issued/new">+ New PDC</Link>
          </Button>
        }
      />
      <ListToolbar search={search} onSearchChange={setSearch} />
      <EnterpriseGrid<PdcIssued>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        listEntity="purchase-pdc-issued"
        isSearching={Boolean(search)}
        pagination={pagination}
        exportCsv={{ ...buildGridExport("pdc-issued", columns), rows: filtered }}
        getRowId={(r) => r.id}
        onRowClick={(r) => router.push(`/purchases/pdc-issued/${r.id}`)}
      />
    </div>
  );
}
