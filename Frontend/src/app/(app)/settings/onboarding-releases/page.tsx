/**
 * Tenant What's New release CMS — P51.
 */
"use client";
import { useTenantListQuery, invalidateTenantQueries } from "@/lib/api/tenant-query";


import { useState } from "react";
import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { WorkspaceLoading } from "@/components/ui/workspace-loading";
import { tourApi } from "@/lib/api/tour";
import { rbacApi } from "@/lib/api/tenant";
import { hasPermission, PERM_USERS_INVITE } from "@/lib/rbac/permissions";

const emptyForm = {
  releaseKey: "",
  title: "",
  summary: "",
  publishedAt: new Date().toISOString().slice(0, 10),
  tourId: "",
  href: "",
  permissions: "",
};

export default function OnboardingReleasesPage() {
  const qc = useQueryClient();
  const [form, setForm] = useState(emptyForm);

  const permsQuery = useTenantListQuery(["my-permissions"], () => rbacApi.getMyPermissions());
  const canManage = hasPermission(permsQuery.data?.result.permissions ?? [], PERM_USERS_INVITE);

  const listQuery = useTenantListQuery(["onboarding-releases"], () => tourApi.listReleases(),
    { enabled: canManage });

  const createMut = useMutation({
    mutationFn: () =>
      tourApi.createRelease({
        releaseKey: form.releaseKey.trim(),
        title: form.title.trim(),
        summary: form.summary.trim(),
        publishedAt: form.publishedAt.trim(),
        tourId: form.tourId.trim() || null,
        href: form.href.trim() || null,
        permissions: form.permissions
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
      }),
    onSuccess: async () => {
      setForm(emptyForm);
      await invalidateTenantQueries(qc, "onboarding-releases");
    },
  });

  const deleteMut = useMutation({
    mutationFn: (dbId: string) => tourApi.deleteRelease(dbId),
    onSuccess: () => invalidateTenantQueries(qc, "onboarding-releases"),
  });

  if (permsQuery.isLoading) return <WorkspaceLoading />;

  if (!canManage) {
    return (
      <div>
        <PageHeader title="What's New releases" breadcrumb="Settings / Releases" />
        <p className="text-sm text-fg-muted">Invite permission required.</p>
      </div>
    );
  }

  const rows = listQuery.data?.result ?? [];

  return (
    <div className="max-w-3xl">
      <PageHeader
        title="What's New releases"
        breadcrumb="Settings / Releases"
        description="Add company-specific updates. Same release key overrides the platform default."
        actions={
          <div className="flex gap-2">
            <Link href="/settings/learning-insights">
              <Button variant="outline" size="sm">
                Learning insights
              </Button>
            </Link>
            <Link href="/settings/platform-releases">
              <Button variant="outline" size="sm">
                Platform releases
              </Button>
            </Link>
          </div>
        }
      />

      <section className="mb-8 rounded-lg border border-border bg-surface p-4">
        <h2 className="text-sm font-semibold text-fg">New release</h2>
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          <FormField label="Release key (slug)">
            <Input
              value={form.releaseKey}
              onChange={(e) => setForm((f) => ({ ...f, releaseKey: e.target.value }))}
              placeholder="2026-06-custom-feature"
            />
          </FormField>
          <FormField label="Published date">
            <Input
              value={form.publishedAt}
              onChange={(e) => setForm((f) => ({ ...f, publishedAt: e.target.value }))}
            />
          </FormField>
          <div className="sm:col-span-2">
            <FormField label="Title">
              <Input
                value={form.title}
                onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
              />
            </FormField>
          </div>
          <div className="sm:col-span-2">
            <FormField label="Summary">
              <Input
                value={form.summary}
                onChange={(e) => setForm((f) => ({ ...f, summary: e.target.value }))}
              />
            </FormField>
          </div>
          <FormField label="Tour id (optional)">
            <Input
              value={form.tourId}
              onChange={(e) => setForm((f) => ({ ...f, tourId: e.target.value }))}
              placeholder="release.invoice-void"
            />
          </FormField>
          <FormField label="Link href (optional)">
            <Input
              value={form.href}
              onChange={(e) => setForm((f) => ({ ...f, href: e.target.value }))}
              placeholder="/sales/invoices"
            />
          </FormField>
          <div className="sm:col-span-2">
            <FormField label="Permissions (comma-separated, empty = all)">
              <Input
                value={form.permissions}
                onChange={(e) => setForm((f) => ({ ...f, permissions: e.target.value }))}
              />
            </FormField>
          </div>
        </div>
        <Button
          type="button"
          className="mt-4"
          disabled={createMut.isPending || !form.releaseKey || !form.title}
          onClick={() => createMut.mutate()}
        >
          {createMut.isPending ? "Saving…" : "Add release"}
        </Button>
        {createMut.error instanceof Error && (
          <p className="mt-2 text-sm text-status-danger">{createMut.error.message}</p>
        )}
      </section>

      <section className="rounded-lg border border-border bg-surface p-4">
        <h2 className="text-sm font-semibold text-fg">Published ({rows.length})</h2>
        {listQuery.isLoading && <p className="mt-2 text-sm text-fg-muted">Loading…</p>}
        <ul className="mt-3 divide-y divide-border">
          {rows.map((row) => (
            <li key={row.dbId} className="flex flex-wrap items-center justify-between gap-2 py-3">
              <div>
                <p className="font-medium text-fg">
                  {row.title}
                  {!row.isActive && (
                    <span className="ml-2 text-xs text-fg-muted">(inactive)</span>
                  )}
                </p>
                <p className="text-xs text-fg-muted">
                  {row.id} · v{row.version} · {row.publishedAt} · {row.source ?? "tenant"}
                </p>
              </div>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                disabled={deleteMut.isPending}
                onClick={() => deleteMut.mutate(row.dbId)}
              >
                Delete
              </Button>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
