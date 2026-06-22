"use client";

import { Button } from "@/components/ui/button";
import { FormSection } from "@/components/ui/form-section";
import { InlineAlert } from "@/components/ui/inline-alert";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { StickyActionBar } from "@/components/ui/sticky-action-bar";
import { cn } from "@/lib/utils";

export interface SummaryLine {
  label: string;
  value: string;
  emphasis?: boolean;
}

interface DocumentWorkspaceProps {
  title: string;
  breadcrumb: string;
  formId: string;
  onSubmit: React.FormEventHandler<HTMLFormElement>;
  isSaving?: boolean;
  isDirty?: boolean;
  saveLabel?: string;
  onCancel: () => void;
  header: React.ReactNode;
  children: React.ReactNode;
  summaryLines: SummaryLine[];
  grandTotalLabel?: string;
  grandTotal: string;
  error?: string | null;
  warning?: string | null;
  statusBadge?: React.ReactNode;
  extraActions?: React.ReactNode;
  topBanner?: React.ReactNode;
  tourRoot?: string;
  tourSummary?: string;
  tourSave?: string;
  demoSandbox?: boolean;
  demoSandboxBanner?: React.ReactNode;
  headerTitle?: string;
  linesTitle?: string;
}

/** Split layout for transactional documents: main form + sticky summary. */
export function DocumentWorkspace({
  title,
  breadcrumb,
  formId,
  onSubmit,
  isSaving,
  isDirty = false,
  saveLabel = "Save",
  onCancel,
  header,
  children,
  summaryLines,
  grandTotalLabel = "Total",
  grandTotal,
  error,
  warning,
  statusBadge,
  extraActions,
  topBanner,
  tourRoot,
  tourSummary,
  tourSave,
  demoSandbox,
  demoSandboxBanner,
  headerTitle = "Document details",
  linesTitle = "Line items",
}: DocumentWorkspaceProps) {
  return (
    <div>
      {demoSandbox && demoSandboxBanner}
      {topBanner}
      <PageHeader
        title={title}
        breadcrumb={breadcrumb}
        tourRoot={tourRoot}
        actions={
          <div className="hidden flex-wrap items-center gap-2 lg:flex">
            {statusBadge}
            {extraActions}
            <Button type="button" variant="outline" onClick={onCancel}>
              Cancel
            </Button>
            <Button
              type="submit"
              form={formId}
              disabled={isSaving || demoSandbox}
              data-tour={tourSave}
              title={demoSandbox ? "Disabled during interactive demo" : undefined}
            >
              {demoSandbox ? "Demo — save disabled" : isSaving ? "Saving…" : saveLabel}
            </Button>
          </div>
        }
      />

      <div className="flex flex-col gap-4 pb-[calc(var(--bottom-nav-height)+env(safe-area-inset-bottom,0px)+4.5rem)] lg:flex-row lg:items-start lg:pb-0">
        <form id={formId} onSubmit={onSubmit} className="min-w-0 flex-1 space-y-4">
          <FormSection title={headerTitle}>{header}</FormSection>
          <FormSection title={linesTitle}>{children}</FormSection>
          {error ? (
            <InlineAlert variant="error" role="alert">
              {error}
            </InlineAlert>
          ) : null}
          {warning ? (
            <InlineAlert variant="warning" role="status">
              {warning}
            </InlineAlert>
          ) : null}
        </form>

        <DocumentSummaryPanel
          summaryLines={summaryLines}
          grandTotalLabel={grandTotalLabel}
          grandTotal={grandTotal}
          tourSummary={tourSummary}
        />
      </div>

      <StickyActionBar
        position="bottom"
        className="bottom-[calc(var(--bottom-nav-height)+env(safe-area-inset-bottom,0px))] justify-between px-safe lg:hidden"
      >
        <div className="flex min-w-0 items-center gap-2 text-sm">
          {isDirty ? (
            <span className="h-2 w-2 shrink-0 rounded-full bg-status-warning" aria-hidden />
          ) : null}
          <span className="truncate text-fg-muted">
            {isDirty ? "Unsaved changes" : grandTotalLabel}:{" "}
            <span className="font-semibold tabular-nums text-fg">{grandTotal}</span>
          </span>
        </div>
        <div className="flex shrink-0 gap-2">
          <Button type="button" size="sm" variant="outline" onClick={onCancel}>
            Cancel
          </Button>
          <Button type="submit" form={formId} size="sm" disabled={isSaving || demoSandbox}>
            {isSaving ? "Saving…" : saveLabel}
          </Button>
        </div>
      </StickyActionBar>
    </div>
  );
}

function DocumentSummaryPanel({
  summaryLines,
  grandTotalLabel,
  grandTotal,
  tourSummary,
}: {
  summaryLines: SummaryLine[];
  grandTotalLabel: string;
  grandTotal: string;
  tourSummary?: string;
}) {
  return (
    <aside
      className="hidden w-72 shrink-0 lg:sticky lg:top-4 lg:block"
      {...(tourSummary ? { "data-tour": tourSummary } : {})}
    >
      <Card variant="elevated" className="p-4">
        <h2 className="mb-3 text-caption font-semibold normal-case tracking-normal text-fg-muted">
          Summary
        </h2>
        <dl className="space-y-2 text-sm">
          {summaryLines.map((line) => (
            <div key={line.label} className="flex justify-between gap-3">
              <dt className="text-fg-muted">{line.label}</dt>
              <dd className={cn("tabular-nums text-fg", line.emphasis && "font-semibold")}>
                {line.value}
              </dd>
            </div>
          ))}
        </dl>
        <div className="divider-soft mt-4" aria-hidden />
        <div className="flex justify-between pt-3 text-sm font-semibold">
          <span>{grandTotalLabel}</span>
          <span className="tabular-nums text-brand-700 dark:text-brand-300">{grandTotal}</span>
        </div>
        <p className="mt-3 text-xs text-fg-muted">
          Totals update as you edit lines. Posting warnings appear after save if GL defaults are missing.
        </p>
      </Card>
    </aside>
  );
}
