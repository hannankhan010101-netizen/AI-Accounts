/** Module entitlement × RBAC matrix — P12. */
"use client";

import { useMemo } from "react";


import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { buildGridExport } from "@/lib/export/grid-export";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { PageHeader } from "@/components/ui/page-header";
import { useClientList } from "@/lib/hooks/use-client-list";
import { matchText } from "@/lib/list/document-list-filters";
import { useTenantReferenceQuery } from "@/lib/api/tenant-query";
import { modulesApi } from "@/lib/api/tenant";


export interface ModuleAccessRow {
  moduleCode: string;
  enabled: boolean;
  requiredPermissions: string[];
  userHasPermission: boolean;
  canAccess: boolean;
  [key: string]: unknown;
}

export default function ModuleAccessPage() {
  const { data, isLoading, error } = useTenantReferenceQuery(["module-access-matrix"], () => modulesApi.accessMatrix());

  const rows = (data?.result ?? []) as ModuleAccessRow[];

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows,
    syncUrl: true,
    filterFn: (r, q) =>
      matchText([r.moduleCode, r.enabled ? "yes" : "no", r.canAccess ? "allowed" : "blocked"], q),
  });

  const columns = useMemo(
    () => responsiveListColumns<ModuleAccessRow>([
      {
        key: "moduleCode",
        header: "Module",
        sortable: true,
        sortAccessor: (r) => r.moduleCode,
        render: (r) => <span className="font-medium capitalize">{r.moduleCode}</span>,
      },
      {
        key: "enabled",
        header: "Licensed",
        render: (r) => (r.enabled ? "Yes" : "No"),
      },
      {
        key: "userHasPermission",
        header: "Role permission",
        render: (r) => (r.userHasPermission ? "Yes" : "No"),
      },
      {
        key: "canAccess",
        header: "Can access",
        render: (r) => (
          <span className={r.canAccess ? "text-status-success" : "font-medium text-status-warning"}>
            {r.canAccess ? "Allowed" : "Blocked"}
          </span>
        ),
      },
    ]),
    [],
  );

  return (
    <div>
      <PageHeader
        title="Module access matrix"
        breadcrumb="Admin / Module access"
        description="Subscription module must be enabled and your role must include a required permission."
      />
      <ListToolbar search={search} onSearchChange={setSearch} />
      <EnterpriseGrid<ModuleAccessRow>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        emptyMessage="No modules configured."
        pagination={pagination}
        exportCsv={{ ...buildGridExport("module-access", columns), rows: filtered }}
        getRowId={(r) => r.moduleCode}
      />
    </div>
  );
}
