"use client";

import { useEffect, useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { invalidateTenantQueries, useTenantReferenceQuery } from "@/lib/api/tenant-query";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { FormField } from "@/components/ui/form-field";
import { PageHeader } from "@/components/ui/page-header";
import { Select } from "@/components/ui/select";
import { WorkspaceLoading } from "@/components/ui/workspace-loading";
import { appSettingsApi } from "@/lib/api/tenant";
import {
  DEFAULT_OP_METHOD_IDS,
  OP_METHOD_CATALOG,
  opMethodLabel,
} from "@/lib/settings/op-methods-catalog";
type OpMethodsSettings = {
  defaultPaymentMethod?: string;
  enabledMethods?: string[];
};

export default function OpMethodsPage() {
  const qc = useQueryClient();
  const [settings, setSettings] = useState<OpMethodsSettings>({
    defaultPaymentMethod: "cash",
    enabledMethods: [...DEFAULT_OP_METHOD_IDS],
  });

  const { data, isLoading, error } = useTenantReferenceQuery(["op-methods-settings"], () => appSettingsApi.getOpMethodsSettings());

  useEffect(() => {
    const raw = data?.result as OpMethodsSettings | undefined;
    if (!raw) return;
    const enabled = Array.isArray(raw.enabledMethods)
      ? raw.enabledMethods.map(String)
      : [...DEFAULT_OP_METHOD_IDS];
    setSettings({
      defaultPaymentMethod: String(raw.defaultPaymentMethod ?? "cash"),
      enabledMethods: enabled.length ? enabled : [...DEFAULT_OP_METHOD_IDS],
    });
  }, [data?.result]);

  const enabledSet = useMemo(
    () => new Set(settings.enabledMethods ?? []),
    [settings.enabledMethods],
  );

  const defaultOptions = OP_METHOD_CATALOG.filter((m) => enabledSet.has(m.id));

  const save = useMutation({
    mutationFn: () => appSettingsApi.putOpMethodsSettings(settings as Record<string, unknown>),
    onSuccess: () => void invalidateTenantQueries(qc, "op-methods-settings"),
  });

  function toggleMethod(id: string, on: boolean) {
    setSettings((prev) => {
      const current = new Set(prev.enabledMethods ?? []);
      if (on) current.add(id);
      else current.delete(id);
      const enabledMethods = [...current];
      let defaultPaymentMethod = prev.defaultPaymentMethod ?? "cash";
      if (!current.has(defaultPaymentMethod)) {
        defaultPaymentMethod = enabledMethods[0] ?? "cash";
      }
      return { ...prev, enabledMethods, defaultPaymentMethod };
    });
  }

  return (
    <div>
      <PageHeader
        title="OP methods"
        breadcrumb="Settings / OP methods"
        description="Payment methods offered on sales receipts and supplier payments (FA §12.1)."
      />
      {isLoading ? <WorkspaceLoading className="mt-4" /> : null}
      {error instanceof Error ? (
        <p className="mt-4 text-sm text-status-danger">{error.message}</p>
      ) : null}
      <section className="mt-4 max-w-lg space-y-5 rounded-lg border border-border bg-surface p-6">
        <FormField label="Default method">
          <Select
            value={settings.defaultPaymentMethod ?? "cash"}
            onChange={(e) =>
              setSettings((s) => ({ ...s, defaultPaymentMethod: e.target.value }))
            }
          >
            {defaultOptions.map((m) => (
              <option key={m.id} value={m.id}>
                {m.label}
              </option>
            ))}
          </Select>
        </FormField>
        <div>
          <p className="mb-2 text-sm font-medium text-fg">Enabled methods</p>
          <div className="space-y-2">
            {OP_METHOD_CATALOG.map((m) => (
              <label key={m.id} className="flex items-center gap-2 text-sm">
                <Checkbox
                  checked={enabledSet.has(m.id)}
                  onChange={(e) => toggleMethod(m.id, e.target.checked)}
                />
                {m.label}
              </label>
            ))}
          </div>
        </div>
        <p className="text-xs text-fg-muted">
          Default: {opMethodLabel(settings.defaultPaymentMethod ?? "cash")} ·{" "}
          {enabledSet.size} method{enabledSet.size === 1 ? "" : "s"} enabled
        </p>
        <Button type="button" disabled={save.isPending || enabledSet.size === 0} onClick={() => save.mutate()}>
          {save.isPending ? "Saving…" : "Save"}
        </Button>
      </section>
    </div>
  );
}
