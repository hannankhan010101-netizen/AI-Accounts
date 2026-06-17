/**
 * Platform-wide What's New CMS — P52 (operators).
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
import { hasPermission, PERM_PLATFORM_PROCESS } from "@/lib/rbac/permissions";

const emptyForm = {
  releaseKey: "",
  title: "",
  summary: "",
  publishedAt: new Date().toISOString().slice(0, 10),
  tourId: "",
  href: "",
  permissions: "",
};

export default function PlatformReleasesPage() {
  const qc = useQueryClient();
  const [form, setForm] = useState(emptyForm);

  const permsQuery = useTenantListQuery(["my-permissions"], () => rbacApi.getMyPermissions());
  const canManage = hasPermission(permsQuery.data?.result.permissions ?? [], PERM_PLATFORM_PROCESS);

  const listQuery = useTenantListQuery(["platform-onboarding-releases"], () => tourApi.listPlatformReleases(),
    { enabled: canManage });

  const createMut = useMutation({
    mutationFn: () =>
      tourApi.createPlatformRelease({
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
      await invalidateTenantQueries(qc, "platform-onboarding-releases");
    },
  });

  const deleteMut = useMutation({
    mutationFn: (dbId: string) => tourApi.deletePlatformRelease(dbId),
    onSuccess: () => invalidateTenantQueries(qc, "platform-onboarding-releases"),
  });

  if (permsQuery.isLoading) return <WorkspaceLoading />;

  if (!canManage) {
    return (
      <div>
        <PageHeader title="Platform releases" breadcrumb="Settings / Platform" />
        <p className="text-sm text-fg-muted">
          Operator permission <code className="text-xs">settings.platform.process</code> required.
        </p>
      </div>
    );
  }

  const rows = listQuery.data?.result ?? [];

  return (
    <div className="max-w-3xl">
      <PageHeader
        title="Platform releases"
        breadcrumb="Settings / Platform releases"
        description="What's New entries for all tenants. Tenant CMS can still override the same release key."
        actions={
          <Link href="/settings/onboarding-releases">
            <Button variant="outline" size="sm">
              Tenant releases
            </Button>
          </Link>
        }
      />

      <section className="mb-8 rounded-lg border border-border bg-surface p-4">
        <h2 className="text-sm font-semibold text-fg">New platform release</h2>
        <div className="mt-4 grid gap-3 sm:grid-cols-2">
          <FormField label="Release key (slug)">
            <Input
              value={form.releaseKey}
              onChange={(e) => setForm((f) => ({ ...f, releaseKey: e.target.value }))}
              placeholder="2026-06-platform-feature"
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
              <Input value={form.title} onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))} />
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
            />
          </FormField>
          <FormField label="Link href (optional)">
            <Input value={form.href} onChange={(e) => setForm((f) => ({ ...f, href: e.target.value }))} />
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
                  {!row.isActive && <span className="ml-2 text-xs text-fg-muted">(inactive)</span>}
                </p>
                <p className="text-xs text-fg-muted">
                  {row.id} · v{row.version} · {row.publishedAt} · platform
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
