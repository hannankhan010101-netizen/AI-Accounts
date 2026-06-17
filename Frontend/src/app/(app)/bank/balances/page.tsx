/** Bank account balances — catalog §4.1 */
"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { buildGridExport } from "@/lib/export/grid-export";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { PageHeader } from "@/components/ui/page-header";
import { useClientList } from "@/lib/hooks/use-client-list";
import { matchText } from "@/lib/list/document-list-filters";
import { bankApi, type BankAccount } from "@/lib/api/tenant";

export default function BankBalancesPage() {
  const { data, isLoading, error } = useTenantListQuery(["bank-accounts"], () => bankApi.listAccounts());

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) => matchText([r.code, r.name, r.currency], q),
  });

  const columns = responsiveListColumns<BankAccount>([
    { key: "code", header: "Code", sortable: true, sortAccessor: (r) => r.code ?? "" },
    { key: "name", header: "Account", sortable: true, sortAccessor: (r) => r.name },
    { key: "currency", header: "Currency" },
    { key: "openingBalance", header: "Opening", align: "right" },
  ]);

  return (
    <div>
      <PageHeader
        title="Account balances"
        breadcrumb="Money / Account balances"
        tourRoot="bank-balances-header"
        tourActions="bank-balances-new"
        actions={
          <Link href="/bank/balances/new">
            <Button>Add account</Button>
          </Link>
        }
      />
      <ListToolbar search={search} onSearchChange={setSearch} />
      <EnterpriseGrid<BankAccount>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        emptyMessage="No bank accounts yet."
        pagination={pagination}
        exportCsv={{ ...buildGridExport("bank-balances", columns), rows: filtered }}
      />
    </div>
  );
}
