"use client";
import { useTenantListQuery, invalidateTenantQueries } from "@/lib/api/tenant-query";


import { useMemo } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { PageHeader } from "@/components/ui/page-header";
import { assemblyApi, type AssemblyJob } from "@/lib/api/tenant";
import { useClientList } from "@/lib/hooks/use-client-list";
import { useConfiguredListColumns } from "@/lib/hooks/use-configured-list-columns";
import { matchText } from "@/lib/list/document-list-filters";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";

export default function AssemblyJobsPage() {
  const qc = useQueryClient();
  const { data, isLoading, error } = useTenantListQuery(["assembly-jobs"], () => assemblyApi.listJobs());

  const finish = useMutation({
    mutationFn: (jobId: string) => assemblyApi.finishJob(jobId),
    onSuccess: () => void invalidateTenantQueries(qc, "assembly-jobs"),
  });

  const { search, setSearch, pageRows, pagination } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) =>
      matchText([r.jobNumber, r.finishedProductCode, r.status], q),
  });

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<AssemblyJob>([
        {
          key: "jobNumber",
          header: "Job no.",
          sortable: true,
          sortAccessor: (r) => r.jobNumber,
          render: (r) => <span className="font-mono">{r.jobNumber}</span>,
        },
        {
          key: "jobDate",
          header: "Date",
          render: (r) => new Date(r.jobDate).toLocaleDateString(),
        },
        { key: "finishedProductCode", header: "Product" },
        { key: "batchNumber", header: "Batch" },
        {
          key: "expiryDate",
          header: "Expiry",
          render: (r) =>
            r.expiryDate ? new Date(String(r.expiryDate)).toLocaleDateString() : "—",
        },
        { key: "quantity", header: "Qty", align: "right" },
        { key: "status", header: "Status" },
        {
          key: "actions",
          header: "",
          render: (r) =>
            r.status === "draft" ? (
              <Button
                size="sm"
                variant="outline"
                disabled={finish.isPending}
                onClick={(e) => {
                  e.stopPropagation();
                  finish.mutate(r.id);
                }}
              >
                Finish
              </Button>
            ) : null,
        },
      ]),
    [finish.isPending],
  );
  const columns = useConfiguredListColumns("assembly-jobs", baseColumns);

  return (
    <div>
      <PageHeader
        title="Assembly jobs"
        breadcrumb="Stock / Assembly / Jobs"
        actions={
          <Link href="/inventory/assembly/jobs/new">
            <Button>New job</Button>
          </Link>
        }
      />
      <ListToolbar search={search} onSearchChange={setSearch} />
      <EnterpriseGrid<AssemblyJob>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        emptyMessage="No assembly jobs yet."
        pagination={pagination}
      />
    </div>
  );
}
