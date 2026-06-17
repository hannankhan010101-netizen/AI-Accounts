/** My Tasks — draft documents needing attention (catalog §2.3). */

"use client";



import Link from "next/link";

import { CheckCircle2 } from "lucide-react";

import { useTenantReferenceQuery } from "@/lib/api/tenant-query";



import { EmptyState } from "@/components/ui/empty-state";

import { InlineAlert } from "@/components/ui/inline-alert";

import { MotionFade } from "@/components/ui/motion-fade";

import { PageHeader } from "@/components/ui/page-header";

import { WorkspaceLoading } from "@/components/ui/workspace-loading";

import { tasksApi } from "@/lib/api/tenant";

import { taskHref } from "@/lib/tasks/task-href";



export default function MyTasksPage() {

  const { data, isLoading, error } = useTenantReferenceQuery(["my-tasks"], () => tasksApi.list());



  const rows = data?.result ?? [];



  return (

    <MotionFade>

      <PageHeader

        title="My tasks"

        breadcrumb="Workspace / My tasks"

        description="Draft documents and items that still need your action."

      />



      {isLoading && <WorkspaceLoading className="mt-4" />}

      {error instanceof Error && (

        <InlineAlert variant="error" className="mt-4">

          {error.message}

        </InlineAlert>

      )}



      {!isLoading && !error && rows.length === 0 && (

        <div className="mt-4 surface-elevated rounded-xl bg-surface dark:border-0">

          <EmptyState

            icon={CheckCircle2}

            title="All caught up"

            description="No open tasks right now. Draft invoices, bills, and other documents will appear here when they need your attention."

          />

        </div>

      )}



      {rows.length > 0 && (

        <ul className="mt-4 overflow-hidden rounded-xl border border-border bg-surface dark:border-0">

          {rows.map((row) => (

            <li key={`${row.entityType}-${row.entityId}`} className="border-b border-border last:border-0">

              <Link

                href={taskHref(row.entityType, row.entityId)}

                className="flex flex-wrap items-center justify-between gap-3 px-4 py-3 text-sm hover:bg-canvas motion-safe-transition"

              >

                <span>

                  <span className="text-label font-medium text-fg">{row.docType}</span>

                  {row.documentNumber && (

                    <span className="ml-2 font-mono text-fg-muted">{row.documentNumber}</span>

                  )}

                  <span className="mt-0.5 block text-caption text-fg-muted">{row.summary}</span>

                </span>

                {row.documentDate && (

                  <span className="shrink-0 text-caption text-fg-muted">

                    {new Date(row.documentDate).toLocaleDateString()}

                  </span>

                )}

              </Link>

            </li>

          ))}

        </ul>

      )}

    </MotionFade>

  );

}

