"use client";

import { useEffect, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { invalidateTenantQueries, useTenantReferenceQuery } from "@/lib/api/tenant-query";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { Select } from "@/components/ui/select";
import { WorkspaceLoading } from "@/components/ui/workspace-loading";
export type SettingsField =
  | { key: string; label: string; kind: "text" | "number" }
  | { key: string; label: string; kind: "checkbox" }
  | { key: string; label: string; kind: "select"; options: { value: string; label: string }[] };

interface ApplicationSettingsFormProps {
  title: string;
  breadcrumb: string;
  description: string;
  queryKey: string;
  fields: SettingsField[];
  load: () => Promise<{ result: Record<string, unknown> }>;
  save: (body: Record<string, unknown>) => Promise<{ result: Record<string, unknown> }>;
}

export function ApplicationSettingsForm({
  title,
  breadcrumb,
  description,
  queryKey,
  fields,
  load,
  save: saveFn,
}: ApplicationSettingsFormProps) {
  const qc = useQueryClient();
  const [draft, setDraft] = useState<Record<string, unknown>>({});

  const { data, isLoading, error } = useTenantReferenceQuery([queryKey], load);

  useEffect(() => {
    if (data?.result) setDraft(data.result);
  }, [data?.result]);

  const save = useMutation({
    mutationFn: () => saveFn(draft),
    onSuccess: () => void invalidateTenantQueries(qc, queryKey),
  });

  function patch(key: string, value: unknown) {
    setDraft((prev) => ({ ...prev, [key]: value }));
  }

  return (
    <div>
      <PageHeader title={title} breadcrumb={breadcrumb} description={description} />
      {isLoading ? <WorkspaceLoading className="mt-4" /> : null}
      {error instanceof Error ? (
        <p className="mt-4 text-sm text-status-danger">{error.message}</p>
      ) : null}
      <section className="mt-4 max-w-xl space-y-4 rounded-lg border border-border bg-surface p-6">
        {fields.map((field) => {
          if (field.kind === "checkbox") {
            return (
              <label key={field.key} className="flex items-center gap-2 text-sm">
                <Checkbox
                  checked={Boolean(draft[field.key])}
                  onChange={(e) => patch(field.key, e.target.checked)}
                />
                {field.label}
              </label>
            );
          }
          if (field.kind === "select") {
            return (
              <FormField key={field.key} label={field.label}>
                <Select
                  value={String(draft[field.key] ?? field.options[0]?.value ?? "")}
                  onChange={(e) => patch(field.key, e.target.value)}
                >
                  {field.options.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </Select>
              </FormField>
            );
          }
          return (
            <FormField key={field.key} label={field.label}>
              <Input
                type={field.kind === "number" ? "number" : "text"}
                value={String(draft[field.key] ?? "")}
                onChange={(e) =>
                  patch(
                    field.key,
                    field.kind === "number" ? Number(e.target.value) : e.target.value,
                  )
                }
              />
            </FormField>
          );
        })}
        <Button type="button" disabled={save.isPending} onClick={() => save.mutate()}>
          {save.isPending ? "Saving…" : "Save"}
        </Button>
      </section>
    </div>
  );
}
