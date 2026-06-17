"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useMemo } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { EnterpriseGrid } from "@/components/ui/enterprise-grid";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { PageHeader } from "@/components/ui/page-header";
import { assemblyApi, type AssemblyTemplate } from "@/lib/api/tenant";
import { useClientList } from "@/lib/hooks/use-client-list";
import { useConfiguredListColumns } from "@/lib/hooks/use-configured-list-columns";
import { matchText } from "@/lib/list/document-list-filters";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";

export default function AssemblyTemplatesPage() {
  const router = useRouter();
  const { data, isLoading, error } = useTenantListQuery(["assembly-templates"], () => assemblyApi.listTemplates());

  const { search, setSearch, pageRows, pagination } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) => matchText([r.code, r.name, r.finishedProductCode], q),
  });

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<AssemblyTemplate>([
        { key: "code", header: "Code", sortable: true, sortAccessor: (r) => r.code },
        { key: "name", header: "Name", sortable: true, sortAccessor: (r) => r.name },
        {
          key: "finishedProductCode",
          header: "Finished product",
          render: (r) => <span className="font-mono text-xs">{r.finishedProductCode}</span>,
        },
        {
          key: "lines",
          header: "Components",
          align: "right",
          render: (r) => r.lines?.length ?? 0,
        },
      ]),
    [],
  );
  const columns = useConfiguredListColumns("assembly-templates", baseColumns);

  return (
    <div>
      <PageHeader
        title="Assembly templates"
        breadcrumb="Stock / Assembly / Templates"
        actions={
          <Link href="/inventory/assembly/templates/new">
            <Button>New template</Button>
          </Link>
        }
      />
      <ListToolbar search={search} onSearchChange={setSearch} />
      <EnterpriseGrid<AssemblyTemplate>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        emptyMessage="No assembly templates yet."
        onRowClick={() => router.push("/inventory/assembly/templates/new")}
        pagination={pagination}
      />
    </div>
  );
}
