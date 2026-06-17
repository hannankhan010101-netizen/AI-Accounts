"use client";
import { useTenantReferenceQuery } from "@/lib/api/tenant-query";



import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { PageHeader } from "@/components/ui/page-header";
import { WorkspaceLoading } from "@/components/ui/workspace-loading";
import { appSettingsApi } from "@/lib/api/tenant";


interface SentEmailRow {
  to?: string;
  subject?: string;
  status?: string;
  sentAt?: string;
  [key: string]: unknown;
}

export default function SentEmailsPage() {
  const { data, isLoading, error } = useTenantReferenceQuery(["sent-emails"], () => appSettingsApi.listSentEmails());

  const rows = (data?.result ?? []) as SentEmailRow[];

  const columns: GridColumn<SentEmailRow>[] = [
    {
      key: "sentAt",
      header: "Sent",
      render: (r) =>
        r.sentAt ? new Date(String(r.sentAt)).toLocaleString() : "—",
    },
    { key: "to", header: "To", render: (r) => String(r.to ?? "—") },
    { key: "subject", header: "Subject", render: (r) => String(r.subject ?? "—") },
    { key: "status", header: "Status", render: (r) => String(r.status ?? "—") },
  ];

  return (
    <div>
      <PageHeader
        title="Sent emails"
        breadcrumb="Settings / Sent emails"
        description="Outbound messages logged when invite or welcome emails are sent successfully."
      />
      {isLoading ? <WorkspaceLoading className="mt-4" /> : null}
      {error instanceof Error ? (
        <p className="mt-4 text-sm text-status-danger">{error.message}</p>
      ) : null}
      {!isLoading && !error ? (
        <div className="mt-4">
        <EnterpriseGrid<SentEmailRow>
          columns={columns}
          rows={rows}
          emptyMessage="No sent emails yet. Resend an invite from Users to record an entry when SMTP is configured."
          getRowId={(r, i) => String(r.sentAt ?? i)}
        />
        </div>
      ) : null}
    </div>
  );
}
