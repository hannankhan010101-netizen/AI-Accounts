/** Full FastAccounts report catalog — all definitions from API with live links. */
"use client";

import Link from "next/link";

import { ReportsDefinitionList } from "@/components/reports/reports-definition-list";
import { PageHeader } from "@/components/ui/page-header";

export default function ReportsCatalogPage() {
  return (
    <>
      <PageHeader
        title="Report catalog"
        breadcrumb="Insights / Full catalog"
        description="Every report definition from the FastAccounts catalog."
        actions={
          <div className="flex flex-wrap gap-2">
            <Link
              href="/reports"
              className="inline-flex h-9 items-center rounded-md border border-border bg-surface px-3 text-sm font-medium text-fg hover:bg-canvas"
            >
              Insights hub
            </Link>
            <Link
              href="/reports/analytical"
              className="inline-flex h-9 items-center rounded-md border border-border bg-surface px-3 text-sm font-medium text-fg hover:bg-canvas"
            >
              Analytical hub
            </Link>
          </div>
        }
      />
      <ReportsDefinitionList />
    </>
  );
}
