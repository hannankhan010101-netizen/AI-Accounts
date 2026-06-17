"use client";
import { useTenantListQuery, invalidateTenantQueries } from "@/lib/api/tenant-query";


import { useRef } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { attachmentsApi } from "@/lib/api/tenant";

export interface AttachmentPanelProps {
  entityType: string;
  entityId: string;
  title?: string;
}

export function AttachmentPanel({
  entityType,
  entityId,
  title = "Attachments",
}: AttachmentPanelProps) {
  const qc = useQueryClient();
  const inputRef = useRef<HTMLInputElement>(null);

  const { data, isLoading } = useTenantListQuery(["attachments", entityType, entityId], () => attachmentsApi.list(entityType, entityId),
    { enabled: Boolean(entityId) });

  const upload = useMutation({
    mutationFn: (file: File) => attachmentsApi.upload(entityType, entityId, file),
    onSuccess: () => {
      void invalidateTenantQueries(qc, "attachments", entityType, entityId);
      if (inputRef.current) inputRef.current.value = "";
    },
  });

  const rows = data?.result ?? [];

  return (
    <section className="rounded-lg border border-border bg-surface p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-sm font-semibold text-fg">{title}</h2>
        <div>
          <input
            ref={inputRef}
            type="file"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) upload.mutate(file);
            }}
          />
          <Button
            type="button"
            size="sm"
            variant="outline"
            disabled={upload.isPending || !entityId}
            onClick={() => inputRef.current?.click()}
          >
            {upload.isPending ? "Uploading…" : "Upload file"}
          </Button>
        </div>
      </div>
      {upload.isError ? (
        <p className="mt-2 text-sm text-status-danger">{(upload.error as Error).message}</p>
      ) : null}
      {isLoading ? (
        <p className="mt-3 text-sm text-fg-muted">Loading…</p>
      ) : rows.length === 0 ? (
        <p className="mt-3 text-sm text-fg-muted">No files attached.</p>
      ) : (
        <ul className="mt-3 space-y-2">
          {rows.map((a) => (
            <li
              key={a.id}
              className="flex items-center justify-between gap-2 rounded border border-border px-3 py-2 text-sm"
            >
              <span className="truncate font-medium">{a.fileName}</span>
              <span className="shrink-0 text-fg-muted">
                {formatBytes(a.byteSize)}
              </span>
              <a
                className="shrink-0 text-brand hover:underline"
                href={attachmentsApi.downloadUrl(a.id)}
                target="_blank"
                rel="noreferrer"
              >
                Download
              </a>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function formatBytes(n: number): string {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}
