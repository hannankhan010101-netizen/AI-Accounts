/** Print template settings — catalog §12.8 (dynamic by document code). */
"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { invalidateTenantQueries, useTenantDetailQuery } from "@/lib/api/tenant-query";

import { PrintTemplateEditor } from "@/components/settings/print-template-editor";
import { PageHeader } from "@/components/ui/page-header";
import { WorkspaceLoading } from "@/components/ui/workspace-loading";
import { printTemplateMeta } from "@/config/print-template-catalog";
import { appSettingsApi, type PrintTemplateSettings } from "@/lib/api/tenant";
export default function PrintTemplateSettingsPage() {
  const params = useParams<{ code: string }>();
  const code = params.code;
  const meta = printTemplateMeta(code);
  const qc = useQueryClient();
  const [draft, setDraft] = useState<PrintTemplateSettings | null>(null);

  const { data, isLoading, error } = useTenantDetailQuery(
    ["print-template", code],
    () => appSettingsApi.getPrintTemplate(code),
    { enabled: Boolean(meta) },
  );

  useEffect(() => {
    if (data?.result) setDraft(data.result);
  }, [data?.result]);

  const save = useMutation({
    mutationFn: () => appSettingsApi.putPrintTemplate(code, draft ?? {}),
    onSuccess: () => {
      void invalidateTenantQueries(qc, "print-template", code);
    },
  });

  if (!meta) {
    return (
      <div>
        <PageHeader title="Print template" breadcrumb="Settings / Printing" />
        <p className="text-sm text-status-danger">Unknown print template code: {code}</p>
        <Link href="/admin" className="mt-4 inline-block text-sm text-brand hover:underline">
          ← Admin settings
        </Link>
      </div>
    );
  }

  return (
    <div>
      <PageHeader
        title={meta.label}
        breadcrumb={`Settings / Printing / ${meta.label}`}
        description={`Configure layout for ${meta.label}. Business logo and address come from Business Information when enabled.`}
        actions={
          <Link
            href="/admin"
            className="inline-flex h-9 items-center rounded-md border border-border bg-surface px-3 text-sm font-medium text-fg hover:bg-canvas"
          >
            Settings menu
          </Link>
        }
      />

      {isLoading ? <WorkspaceLoading className="mt-4" /> : null}
      {error instanceof Error ? (
        <p className="mt-4 text-sm text-status-danger">{error.message}</p>
      ) : null}

      {draft ? (
        <PrintTemplateEditor
          meta={meta}
          value={draft}
          onChange={setDraft}
          onSave={() => save.mutate()}
          saving={save.isPending}
        />
      ) : null}
    </div>
  );
}
