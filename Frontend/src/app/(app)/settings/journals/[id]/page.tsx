/** Journal voucher detail — catalog §9.2. */
"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { invalidateTenantQueries, useTenantDetailQuery } from "@/lib/api/tenant-query";
import Decimal from "decimal.js";

import { StatusBadge } from "@/components/app/status-badge";
import { AttachmentPanel } from "@/components/patterns/attachment-panel";
import { PrintLink } from "@/components/print/print-link";
import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { PageHeader } from "@/components/ui/page-header";
import { journalsApi, type JournalLine } from "@/lib/api/tenant";
import { DetailPageLoading } from "@/components/ui/detail-page-loading";

function fmt(v: string | number | undefined | null): string {
  if (v === undefined || v === null || v === "") return "—";
  try {
    return new Decimal(typeof v === "string" ? v : v.toString()).toFixed(2);
  } catch {
    return String(v);
  }
}

export default function JournalDetailPage() {
  const params = useParams();
  const router = useRouter();
  const queryClient = useQueryClient();
  const id = typeof params.id === "string" ? params.id : "";

  const { data, isLoading, error } = useTenantDetailQuery(["journal", id], () => journalsApi.get(id), { enabled: Boolean(id) });

  const journal = data?.result;
  const lines = journal?.lines ?? [];

  const copyJournal = useMutation({
    mutationFn: () => journalsApi.copy(id),
    onSuccess: (res) => {
      void invalidateTenantQueries(queryClient, "journals");
      router.push(`/settings/journals/${res.result.id}`);
    },
  });

  const reverseJournal = useMutation({
    mutationFn: () =>
      journalsApi.reverse(id, { reversalDate: new Date().toISOString().slice(0, 10) }),
    onSuccess: (res) => {
      void invalidateTenantQueries(queryClient, "journal", id);
      void invalidateTenantQueries(queryClient, "journals");
      router.push(`/settings/journals/${res.result.id}`);
    },
  });

  const columns = responsiveListColumns<JournalLine>([
    { key: "nominalCode", header: "Nominal", sortable: true },
    {
      key: "debit",
      header: "Debit",
      align: "right",
      sortable: true,
      sortAccessor: (r) => Number(r.debit),
      render: (r) => fmt(r.debit),
    },
    {
      key: "credit",
      header: "Credit",
      align: "right",
      sortable: true,
      sortAccessor: (r) => Number(r.credit),
      render: (r) => fmt(r.credit),
    },
    {
      key: "projectCode",
      header: "Project",
      render: (r) => r.projectCode ?? "—",
    },
  ]);

  if (isLoading) return <DetailPageLoading />;
  if (!journal) return null;

  const ref = journal.refNo ?? journal.reference ?? "—";
  const total = journal.totalAmount ?? journal.totalDebit;

  return (
    <div>
      <PageHeader
        title={`Journal ${journal.journalNumber ?? id}`}
        breadcrumb="Accounting / Journals / Detail"
        actions={
          <div className="flex gap-2">
            {journal.status === "draft" ? (
              <Link href={`/settings/journals/${id}/edit`}>
                <Button type="button" variant="secondary">
                  Edit draft
                </Button>
              </Link>
            ) : null}
            <Button
              type="button"
              variant="outline"
              disabled={copyJournal.isPending}
              onClick={() => copyJournal.mutate()}
            >
              {copyJournal.isPending ? "Copying…" : "Copy"}
            </Button>
            {journal.status !== "reversed" ? (
              <Button
                type="button"
                variant="secondary"
                disabled={reverseJournal.isPending}
                onClick={() => {
                  if (window.confirm("Reverse this journal? A storno entry will be created.")) {
                    reverseJournal.mutate();
                  }
                }}
              >
                {reverseJournal.isPending ? "Reversing…" : "Reverse"}
              </Button>
            ) : null}
            <PrintLink href={`/print/journal/${id}`} />
            <Link href="/settings/journals">
              <Button variant="outline">Back to list</Button>
            </Link>
          </div>
        }
      />

      <section className="mb-6 grid grid-cols-2 gap-4 rounded-lg border border-border bg-surface p-4 md:grid-cols-4">
        <Field label="Date" value={new Date(journal.journalDate).toLocaleDateString()} />
        <Field label="Reference" value={ref} />
        <Field label="Total" value={fmt(total)} />
        <div>
          <div className="text-xs font-medium uppercase tracking-wide text-fg-muted">Status</div>
          <div className="mt-1">
            <StatusBadge status={journal.status ?? "posted"} />
          </div>
        </div>
        {journal.sourceType ? (
          <Field label="Source" value={`${journal.sourceType}${journal.sourceId ? ` · ${journal.sourceId}` : ""}`} />
        ) : null}
      </section>

      <EnterpriseGrid<JournalLine>
        columns={columns}
        rows={lines}
        loading={isLoading}
        error={error}
        emptyMessage="No lines on this journal."
        getRowId={(r) => r.id}
      />

      <AttachmentPanel entityType="journal" entityId={id} title="Attachments" />
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs font-medium uppercase tracking-wide text-fg-muted">{label}</div>
      <div className="mt-1 text-sm font-medium text-fg">{value}</div>
    </div>
  );
}
