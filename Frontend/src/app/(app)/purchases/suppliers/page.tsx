/** Suppliers list — catalog §6.1 */
"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useMemo } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { EnterpriseGrid } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { useConfiguredListColumns } from "@/lib/hooks/use-configured-list-columns";
import { buildGridExport } from "@/lib/export/grid-export";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { PageHeader } from "@/components/ui/page-header";
import { useClientList } from "@/lib/hooks/use-client-list";
import { matchText } from "@/lib/list/document-list-filters";
import { partiesApi, type Supplier } from "@/lib/api/tenant";

export default function SuppliersPage() {
  const { data, isLoading, error } = useTenantListQuery(["suppliers"], () => partiesApi.listSuppliers());

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) => matchText([r.code, r.name, r.email, r.phone], q),
  });

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<Supplier>([
        { key: "code", header: "Code", sortable: true, sortAccessor: (r) => r.code ?? "" },
        { key: "name", header: "Supplier", sortable: true, sortAccessor: (r) => r.name },
        { key: "email", header: "Email" },
        { key: "phone", header: "Phone" },
      ]),
    [],
  );

  const columns = useConfiguredListColumns("suppliers", baseColumns);

  return (
    <div>
      <PageHeader
        title="Suppliers"
        breadcrumb="Buy / Suppliers"
        actions={
          <Button asChild>
            <Link href="/purchases/suppliers/new">Add supplier</Link>
          </Button>
        }
      />
      <ListToolbar search={search} onSearchChange={setSearch} />
      <EnterpriseGrid<Supplier>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        listEntity="purchase-supplier"
        isSearching={Boolean(search)}
        pagination={pagination}
        exportCsv={{ ...buildGridExport("suppliers", columns), rows: filtered }}
      />
    </div>
  );
}
