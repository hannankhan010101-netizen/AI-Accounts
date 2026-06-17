"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { invalidateTenantQueries, useTenantReferenceQuery } from "@/lib/api/tenant-query";

import { Button } from "@/components/ui/button";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { templatesApi } from "@/lib/api/tenant";
import { useState } from "react";

interface TransactionTemplatePickerProps {
  module: string;
  onLoad: (payload: Record<string, unknown>) => void;
  onCapturePayload: () => Record<string, unknown>;
}

export function TransactionTemplatePicker({
  module,
  onLoad,
  onCapturePayload,
}: TransactionTemplatePickerProps) {
  const qc = useQueryClient();
  const [saveName, setSaveName] = useState("");
  const [selectedId, setSelectedId] = useState("");

  const { data, isLoading } = useTenantReferenceQuery(["transaction-templates", module], () => templatesApi.list(module));

  const templates = data?.result ?? [];

  const save = useMutation({
    mutationFn: () =>
      templatesApi.create({
        module,
        name: saveName.trim(),
        payload: onCapturePayload(),
      }),
    onSuccess: () => {
      setSaveName("");
      void invalidateTenantQueries(qc, "transaction-templates", module);
    },
  });

  const load = useMutation({
    mutationFn: (id: string) => templatesApi.get(id),
    onSuccess: (res) => {
      if (res.result?.payload && typeof res.result.payload === "object") {
        onLoad(res.result.payload as Record<string, unknown>);
      }
    },
  });

  const remove = useMutation({
    mutationFn: (id: string) => templatesApi.remove(id),
    onSuccess: () => {
      setSelectedId("");
      void invalidateTenantQueries(qc, "transaction-templates", module);
    },
  });

  return (
    <section className="mb-4 rounded-lg border border-border bg-canvas/40 p-4">
      <h3 className="mb-3 text-sm font-semibold text-fg">Templates</h3>
      <div className="flex flex-wrap items-end gap-3">
        <FormField label="Load template">
          <Select
            value={selectedId}
            disabled={isLoading}
            onChange={(e) => setSelectedId(e.target.value)}
          >
            <option value="">Select…</option>
            {templates.map((t) => (
              <option key={t.id} value={t.id}>
                {t.name}
              </option>
            ))}
          </Select>
        </FormField>
        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={!selectedId || load.isPending}
          onClick={() => load.mutate(selectedId)}
        >
          Load
        </Button>
        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={!selectedId || remove.isPending}
          onClick={() => remove.mutate(selectedId)}
        >
          Delete
        </Button>
        <FormField label="Save as">
          <Input
            value={saveName}
            onChange={(e) => setSaveName(e.target.value)}
            placeholder="Template name"
          />
        </FormField>
        <Button
          type="button"
          size="sm"
          disabled={!saveName.trim() || save.isPending}
          onClick={() => save.mutate()}
        >
          Save template
        </Button>
      </div>
    </section>
  );
}
