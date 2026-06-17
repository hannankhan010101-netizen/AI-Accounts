"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import type { ReactNode } from "react";

import { StatusBadge } from "@/components/app/status-badge";
import { AttachmentPanel } from "@/components/patterns/attachment-panel";
import { PrintLink } from "@/components/print/print-link";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";

export interface BankVoucherField {
  label: string;
  value: string;
  emphasis?: boolean;
}

interface BankVoucherDetailProps {
  title: string;
  breadcrumb: string;
  listHref: string;
  fields: BankVoucherField[];
  journalId?: string | null;
  printHref?: string;
  voucherId?: string;
  attachmentEntityType?: "bank_payment" | "bank_receipt" | "bank_transfer";
  extraActions?: ReactNode;
}

export function BankVoucherDetail({
  title,
  breadcrumb,
  listHref,
  fields,
  journalId,
  printHref,
  voucherId,
  attachmentEntityType,
  extraActions,
}: BankVoucherDetailProps) {
  const router = useRouter();

  return (
    <div>
      <PageHeader
        title={title}
        breadcrumb={breadcrumb}
        actions={
          <div className="flex gap-2">
            {extraActions}
            {printHref ? <PrintLink href={printHref} /> : null}
            <Button type="button" variant="outline" onClick={() => router.push(listHref)}>
              Back
            </Button>
          </div>
        }
      />

      <section className="grid grid-cols-1 gap-4 rounded-lg border border-border bg-surface p-4 md:grid-cols-4">
        {fields.map((f) => (
          <div key={f.label}>
            <div className="text-xs font-medium uppercase tracking-wide text-fg-muted">
              {f.label}
            </div>
            <div
              className={`mt-1 text-sm ${f.emphasis ? "font-semibold text-fg" : "font-medium text-fg"}`}
            >
              {f.value}
            </div>
          </div>
        ))}
        <div>
          <div className="text-xs font-medium uppercase tracking-wide text-fg-muted">Posted</div>
          <div className="mt-1 flex flex-col gap-1">
            <StatusBadge status={journalId ? "posted" : "draft"} />
            {journalId ? (
              <Link
                href={`/settings/journals/${journalId}`}
                className="text-sm text-brand hover:underline"
              >
                View journal
              </Link>
            ) : (
              <span className="text-sm text-fg-muted">No GL journal</span>
            )}
          </div>
        </div>
      </section>

      {attachmentEntityType && voucherId ? (
        <AttachmentPanel
          entityType={attachmentEntityType}
          entityId={voucherId}
          title="Attachments"
        />
      ) : null}
    </div>
  );
}
