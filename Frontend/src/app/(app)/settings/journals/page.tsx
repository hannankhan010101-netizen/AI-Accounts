/** Journals list — catalog §9.2.1 */
"use client";
import { useTenantListQuery, invalidateTenantQueries } from "@/lib/api/tenant-query";


import { useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { buildGridExport } from "@/lib/export/grid-export";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { PageHeader } from "@/components/ui/page-header";
import { useClientList } from "@/lib/hooks/use-client-list";
import { useConfiguredListColumns } from "@/lib/hooks/use-configured-list-columns";
import { matchText } from "@/lib/list/document-list-filters";
import { ApiError } from "@/lib/api/client";
import { journalsApi, ledgerApi, type Journal } from "@/lib/api/tenant";

export default function JournalsPage() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const [bulkError, setBulkError] = useState<string | null>(null);
  const { data, isLoading, error } = useTenantListQuery(["journals"], () => ledgerApi.listJournals());

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) => matchText([r.journalNumber, r.refNo, r.reference], q),
  });

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<Journal>([
        {
          key: "journalNumber",
          header: "Journal ID",
          sortable: true,
          sortAccessor: (r) => r.journalNumber ?? "",
        },
        {
          key: "journalDate",
          header: "Date",
          sortable: true,
          sortAccessor: (r) => r.journalDate,
          render: (r) => new Date(r.journalDate).toLocaleDateString(),
        },
        {
          key: "refNo",
          header: "Reference",
          sortable: true,
          sortAccessor: (r) => r.refNo ?? r.reference ?? "",
          render: (r) => r.refNo ?? r.reference ?? "—",
        },
        {
          key: "totalAmount",
          header: "Total",
          align: "right",
          sortable: true,
          sortAccessor: (r) => Number(r.totalAmount ?? r.totalDebit ?? 0),
          render: (r) => String(r.totalAmount ?? r.totalDebit ?? "—"),
        },
      ]),
    [],
  );
  const columns = useConfiguredListColumns("journals", baseColumns);

  const deletableDraftIds = useMemo(
    () =>
      (filtered ?? []).filter(
        (j) =>
          (j.status ?? "").toLowerCase() === "draft" &&
          !j.sourceType &&
          !j.sourceId &&
          j.id,
      ).map((j) => j.id as string),
    [filtered],
  );

  const bulkDeleteMutation = useMutation({
    mutationFn: () => journalsApi.bulkDelete(deletableDraftIds),
    onSuccess: async (res) => {
      setBulkError(null);
      await invalidateTenantQueries(queryClient, "journals");
      const skipped = res.result?.skipped ?? 0;
      if (skipped > 0) {
        setBulkError(
          `Deleted ${res.result?.deleted ?? 0} draft(s); ${skipped} skipped (posted or system-linked).`,
        );
      }
    },
    onError: (err) =>
      setBulkError(err instanceof ApiError ? err.message : "Could not delete drafts"),
  });

  return (
    <div>
      <PageHeader
        title="Journals"
        breadcrumb="Accounting / Journals"
        tourRoot="journals-header"
        tourActions="journals-new"
        actions={
          <div className="flex flex-wrap items-center gap-2">
            {deletableDraftIds.length > 0 ? (
              <Button
                variant="outline"
                disabled={bulkDeleteMutation.isPending}
                onClick={() => {
                  if (
                    window.confirm(
                      `Delete ${deletableDraftIds.length} manual draft journal(s)? This cannot be undone.`,
                    )
                  ) {
                    bulkDeleteMutation.mutate();
                  }
                }}
              >
                Delete draft journals ({deletableDraftIds.length})
              </Button>
            ) : null}
            <Link href="/settings/journals/new">
              <Button>New journal</Button>
            </Link>
          </div>
        }
      />
      {bulkError ? (
        <p className="mb-3 text-sm text-amber-700 dark:text-amber-400" role="status">
          {bulkError}
        </p>
      ) : null}
      <ListToolbar search={search} onSearchChange={setSearch} />
      <EnterpriseGrid<Journal>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        emptyMessage="No journals yet."
        onRowClick={(r) => r.id && router.push(`/settings/journals/${r.id}`)}
        pagination={pagination}
        exportCsv={{ ...buildGridExport("journals", columns), rows: filtered }}
      />
    </div>
  );
}
