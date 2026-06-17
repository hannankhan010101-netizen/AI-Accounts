/** Customers list — catalog §5.1 */
"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useMemo } from "react";
import Link from "next/link";
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
import { partiesApi, type Customer } from "@/lib/api/tenant";

export default function CustomersPage() {
  const { data, isLoading, error } = useTenantListQuery(["customers"], () => partiesApi.listCustomers());

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) => matchText([r.code, r.name, r.email, r.phone], q),
  });

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<Customer>([
        { key: "code", header: "Code", sortable: true, sortAccessor: (r) => r.code ?? "" },
        { key: "name", header: "Customer", sortable: true, sortAccessor: (r) => r.name },
        { key: "email", header: "Email" },
        { key: "phone", header: "Phone" },
      ]),
    [],
  );
  const columns = useConfiguredListColumns("customers", baseColumns);

  return (
    <div>
      <PageHeader
        title="Customers"
        breadcrumb="Sell / Customers"
        actions={
          <Button asChild>
            <Link href="/sales/customers/new">Add customer</Link>
          </Button>
        }
      />
      <ListToolbar search={search} onSearchChange={setSearch} searchPlaceholder="Search customers…" />
      <EnterpriseGrid<Customer>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        listEntity="sales-customer"
        isSearching={Boolean(search)}
        pagination={pagination}
        exportCsv={{ ...buildGridExport("customers", columns), rows: filtered }}
      />
    </div>
  );
}
