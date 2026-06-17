"use client";
import { useTenantReferenceQuery, invalidateTenantQueries } from "@/lib/api/tenant-query";

import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { WorkspaceLoading } from "@/components/ui/workspace-loading";
import { rbacApi, settingsApi } from "@/lib/api/tenant";
import { referenceQueryOptions } from "@/lib/query/options";

interface FormValues {
  globalLockDate: string;
}

interface PerUserRow {
  userId: string;
  label: string;
  extendedLockDate: string;
}

export default function LockDatePage() {
  const qc = useQueryClient();
  const [savedAt, setSavedAt] = useState<Date | null>(null);
  const [perUser, setPerUser] = useState<PerUserRow[]>([]);

  const { data, isLoading } = useTenantReferenceQuery(["lock-date"], () => settingsApi.getLockDate());

  const usersQuery = useTenantReferenceQuery(["rbac-users-lock-date"], () => rbacApi.listUsers({ page: 1, pageSize: 200 }));

  const form = useForm<FormValues>({ defaultValues: { globalLockDate: "" } });

  useEffect(() => {
    if (data?.result?.globalLockDate) {
      form.reset({ globalLockDate: data.result.globalLockDate.slice(0, 10) });
    }
    const extensions = (
      data?.result as { perUserExtensions?: { userId: string; extendedLockDate?: string | null }[] }
    )?.perUserExtensions;
    const users = usersQuery.data?.result?.items ?? [];
    if (users.length) {
      const extMap = new Map(
        (extensions ?? []).map((e) => [e.userId, e.extendedLockDate?.slice(0, 10) ?? ""]),
      );
      setPerUser(
        users.map((u) => ({
          userId: String(u.userId ?? u.id),
          label:
            `${u.firstName ?? ""} ${u.lastName ?? ""}`.trim() || String(u.email ?? u.userId),
          extendedLockDate: extMap.get(String(u.userId ?? u.id)) ?? "",
        })),
      );
    }
  }, [data, usersQuery.data, form]);

  const mutation = useMutation({
    mutationFn: (values: FormValues) =>
      settingsApi.putLockDate({
        globalLockDate: values.globalLockDate ? values.globalLockDate : null,
      }),
    onSuccess: () => {
      setSavedAt(new Date());
      invalidateTenantQueries(qc, "lock-date");
    },
  });

  const savePerUser = useMutation({
    mutationFn: async () => {
      for (const row of perUser) {
        if (!row.extendedLockDate) continue;
        await settingsApi.putLockDatePerUser(row.userId, row.extendedLockDate);
      }
    },
    onSuccess: () => invalidateTenantQueries(qc, "lock-date"),
  });

  return (
    <div>
      <PageHeader
        title="Lock Date"
        breadcrumb="Home / Lock Date"
        description="Block edits on or before the global lock date. Per-user extensions allow selected users to post in an earlier period (§9.5)."
      />

      {isLoading || usersQuery.isLoading ? (
        <WorkspaceLoading />
      ) : (
        <div className="space-y-8">
          <form
            onSubmit={form.handleSubmit((v) => mutation.mutate(v))}
            className="max-w-md space-y-4 rounded-lg border border-border bg-surface p-6"
          >
            <FormField label="Global lock date" htmlFor="globalLockDate">
              <Input id="globalLockDate" type="date" {...form.register("globalLockDate")} />
            </FormField>

            <div className="flex items-center gap-2">
              <Button type="submit" disabled={mutation.isPending}>
                {mutation.isPending ? "Saving…" : "Save global"}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => form.reset({ globalLockDate: "" })}
              >
                Clear
              </Button>
            </div>

            {savedAt ? (
              <div className="text-xs text-status-success">
                Saved at {savedAt.toLocaleTimeString()}
              </div>
            ) : null}
          </form>

          <section className="max-w-2xl space-y-4 rounded-lg border border-border bg-surface p-6">
            <h2 className="text-sm font-semibold text-fg">Per-user extensions</h2>
            <p className="text-xs text-fg-muted">
              Users with an earlier extension date can post documents after that date even when the
              global lock is later.
            </p>
            <div className="space-y-3">
              {perUser.map((row, index) => (
                <div key={row.userId} className="flex flex-wrap items-end gap-3">
                  <FormField label={row.label}>
                    <Input
                      type="date"
                      value={row.extendedLockDate}
                      onChange={(e) =>
                        setPerUser((prev) =>
                          prev.map((r, i) =>
                            i === index ? { ...r, extendedLockDate: e.target.value } : r,
                          ),
                        )
                      }
                    />
                  </FormField>
                </div>
              ))}
            </div>
            <Button
              type="button"
              disabled={savePerUser.isPending}
              onClick={() => savePerUser.mutate()}
            >
              {savePerUser.isPending ? "Saving…" : "Save per-user dates"}
            </Button>
          </section>
        </div>
      )}
    </div>
  );
}
