"use client";

import { PageHeader } from "@/components/ui/page-header";
import { InlineAlert } from "@/components/ui/inline-alert";
import { cn } from "@/lib/utils";

export type DetailMetaField = {
  label: string;
  value: React.ReactNode;
  className?: string;
};

type DocumentDetailShellProps = {
  title: string;
  breadcrumb: string;
  actions?: React.ReactNode;
  statusBadge?: React.ReactNode;
  metaFields: DetailMetaField[];
  banners?: React.ReactNode;
  children: React.ReactNode;
  tourRoot?: string;
};

/** Shared read-only document layout: header, meta grid, alerts, sections. */
export function DocumentDetailShell({
  title,
  breadcrumb,
  actions,
  statusBadge,
  metaFields,
  banners,
  children,
  tourRoot,
}: DocumentDetailShellProps) {
  return (
    <div className="space-y-4">
      <PageHeader
        title={title}
        breadcrumb={breadcrumb}
        tourRoot={tourRoot}
        actions={
          <div className="flex flex-wrap items-center gap-2">
            {statusBadge}
            {actions}
          </div>
        }
      />
      {banners}
      <section className="surface-elevated grid grid-cols-1 gap-4 rounded-xl bg-surface p-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 dark:border-0">
        {metaFields.map((field) => (
          <div key={field.label} className={cn("min-w-0", field.className)}>
            <div className="text-caption text-fg-muted">{field.label}</div>
            <div className="mt-1 text-sm text-fg">{field.value}</div>
          </div>
        ))}
      </section>
      <div className="space-y-4">{children}</div>
    </div>
  );
}

export function DetailAlertBanner({
  variant,
  children,
}: {
  variant: "success" | "error" | "warning" | "info";
  children: React.ReactNode;
}) {
  const mapped =
    variant === "success"
      ? "success"
      : variant === "error"
        ? "error"
        : variant === "warning"
          ? "warning"
          : "info";
  return (
    <InlineAlert variant={mapped} role="alert" className="mb-0">
      {children}
    </InlineAlert>
  );
}
