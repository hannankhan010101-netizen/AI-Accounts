/** ERP data migration wizard — mapping, preview, import dashboard. */
"use client";
import { useTenantListQuery, invalidateTenantQueries } from "@/lib/api/tenant-query";


import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useCallback, useMemo, useState } from "react";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { Select } from "@/components/ui/select";
import { WizardShell } from "@/components/ui/wizard-shell";
import {
  migrationsApi,
  type EntityModule,
  type MappingRule,
  type MigrationRun,
} from "@/lib/api/migrations";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";

const MODULES: EntityModule[] = [
  "customers",
  "suppliers",
  "products",
  "chart_of_accounts",
  "invoices",
  "bills",
  "receipts",
  "payments",
  "bank_transactions",
  "journals",
  "taxes",
  "projects",
  "stock_movements",
];

const SOURCE_TYPES = [
  { value: "csv", label: "CSV file" },
  { value: "xlsx", label: "Excel file" },
  { value: "fastaccounts", label: "FastAccounts export (JSON)" },
  { value: "json", label: "JSON" },
  { value: "api", label: "API pull" },
];

type WizardStep = "module" | "upload" | "mapping" | "preview" | "import";

const WIZARD_STEPS = [
  { id: "module", label: "Module" },
  { id: "upload", label: "Upload" },
  { id: "mapping", label: "Mapping" },
  { id: "preview", label: "Preview" },
  { id: "import", label: "Import" },
] as const;

const STEP_META: Record<WizardStep, { title: string; description: string }> = {
  module: {
    title: "Choose module and source",
    description: "Select what you are importing and where the data comes from.",
  },
  upload: {
    title: "Upload source file",
    description: "Drag and drop a CSV, Excel, or JSON export to inspect columns.",
  },
  mapping: {
    title: "Map source fields",
    description: "Match source columns to FastAccounts fields. Use auto-suggest when available.",
  },
  preview: {
    title: "Validate preview",
    description: "Review transformed rows and fix mapping errors before starting the import.",
  },
  import: {
    title: "Import in progress",
    description: "Track run progress below. You can leave this page while the job completes.",
  },
};

export default function MigrationsPage() {
  const qc = useQueryClient();
  const [step, setStep] = useState<WizardStep>("module");
  const [module, setModule] = useState<EntityModule>("customers");
  const [sourceType, setSourceType] = useState("csv");
  const [file, setFile] = useState<File | null>(null);
  const [sourceFields, setSourceFields] = useState<string[]>([]);
  const [rules, setRules] = useState<MappingRule[]>([]);
  const [sampleRows, setSampleRows] = useState<Record<string, unknown>[]>([]);
  const [runId, setRunId] = useState<string | null>(null);
  const [profileId, setProfileId] = useState<string | null>(null);

  const { data: runs, isLoading } = useTenantListQuery(
    ["migration-runs"],
    () => migrationsApi.list(),
    { refetchInterval: 5000 },
  );

  const { data: targetSchema } = useTenantListQuery(
    ["target-schema", module],
    () => migrationsApi.getTargetSchema(module),
    { enabled: step === "mapping" || step === "preview" },
  );

  const createProfile = useMutation({
    mutationFn: (): Promise<{ result: { id: string } }> =>
      migrationsApi.createMappingProfile({
        name: `${module}-${sourceType}`,
        module,
        sourceSystem: sourceType === "fastaccounts" ? "fastaccounts" : "generic",
        rules,
      }) as Promise<{ result: { id: string } }>,
    onSuccess: (res) => {
      setProfileId(res.result.id);
    },
  });

  const suggest = useMutation({
    mutationFn: async () => {
      let pid = profileId;
      if (!pid) {
        const created = (await createProfile.mutateAsync()) as { result: { id: string } };
        pid = created.result.id;
        setProfileId(pid);
      }
      return migrationsApi.suggestMappings(
        pid!,
        sourceFields,
        sourceType === "fastaccounts" ? "fastaccounts" : "generic",
      );
    },
    onSuccess: (res) => {
      setRules(res.result.proposedRules);
    },
  });

  const preview = useMutation({
    mutationFn: () =>
      migrationsApi.preview({ module, rules, rows: sampleRows.slice(0, 50) }),
  });

  const startImport = useMutation({
    mutationFn: async () => {
      const run = await migrationsApi.createRun({
        name: `Import ${module} ${new Date().toLocaleDateString()}`,
        module,
        sourceType,
        sourceSystem: sourceType === "fastaccounts" ? "fastaccounts" : "generic",
        mappingProfileId: profileId ?? undefined,
      });
      setRunId(run.result.id);
      if (file && sourceType === "csv") {
        await migrationsApi.uploadCsv(run.result.id, file);
      } else {
        await migrationsApi.startRun(run.result.id);
      }
      return run.result;
    },
    onSuccess: () => {
      setStep("import");
      void invalidateTenantQueries(qc, "migration-runs");
    },
  });

  const parseFilePreview = useCallback(async (f: File) => {
    const text = await f.text();
    const lines = text.split(/\r?\n/).filter(Boolean);
    if (lines.length < 2) return;
    const headers = lines[0].split(",").map((h) => h.trim().replace(/^"|"$/g, ""));
    setSourceFields(headers);
    const rows: Record<string, unknown>[] = [];
    for (let i = 1; i < Math.min(lines.length, 51); i++) {
      const cols = lines[i].split(",").map((c) => c.trim().replace(/^"|"$/g, ""));
      const row: Record<string, unknown> = {};
      headers.forEach((h, j) => {
        row[h] = cols[j] ?? "";
      });
      rows.push(row);
    }
    setSampleRows(rows);
  }, []);

  const onFileChange = (f: File | null) => {
    setFile(f);
    if (f) void parseFilePreview(f);
  };

  const runColumns = useMemo(
    (): GridColumn<MigrationRun>[] => [
      { key: "name", header: "Name" },
      { key: "module", header: "Module" },
      { key: "status", header: "Status" },
      { key: "currentStage", header: "Stage" },
      {
        key: "progress",
        header: "Progress",
        render: (r) => {
          const total = Number(r.totalRows ?? 0);
          const done = Number(r.processedRows ?? 0);
          return total ? `${done}/${total}` : "—";
        },
      },
      {
        key: "errors",
        header: "Errors",
        render: (r) => String(r.errorRows ?? 0),
      },
    ],
    [],
  );

  return (
    <div className="space-y-6">
      <PageHeader
        title="Data Migration"
        description="Import customers, suppliers, invoices, inventory, and more from CSV, Excel, or FastAccounts."
      />

      <WizardShell
        steps={[...WIZARD_STEPS]}
        currentStepId={step}
        title={STEP_META[step].title}
        description={STEP_META[step].description}
      >
        {step === "module" && (
          <div className="flex flex-wrap gap-4">
            <label className="flex flex-col gap-1 text-sm">
              Module
              <Select value={module} onChange={(e) => setModule(e.target.value as EntityModule)}>
                {MODULES.map((m) => (
                  <option key={m} value={m}>
                    {m.replace(/_/g, " ")}
                  </option>
                ))}
              </Select>
            </label>
            <label className="flex flex-col gap-1 text-sm">
              Source
              <Select value={sourceType} onChange={(e) => setSourceType(e.target.value)}>
                {SOURCE_TYPES.map((s) => (
                  <option key={s.value} value={s.value}>
                    {s.label}
                  </option>
                ))}
              </Select>
            </label>
            <Button className="self-end" onClick={() => setStep("upload")}>
              Next
            </Button>
          </div>
        )}

        {step === "upload" && (
          <div className="space-y-4">
            <div
              className="flex min-h-[120px] cursor-pointer flex-col items-center justify-center rounded-md border-2 border-dashed p-6"
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault();
                const f = e.dataTransfer.files[0];
                if (f) onFileChange(f);
              }}
            >
              <p className="text-sm text-fg-muted">
                Drag & drop CSV/XLSX, or choose a file
              </p>
              <input
                type="file"
                accept=".csv,.xlsx,.json"
                className="mt-2 text-sm"
                onChange={(e) => onFileChange(e.target.files?.[0] ?? null)}
              />
              {file && <p className="mt-2 text-sm">{file.name}</p>}
            </div>
            {sourceType === "fastaccounts" && (
              <p className="text-sm text-fg-muted">
                FastAccounts labeled JSON path is configured when starting the run on the server.
              </p>
            )}
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setStep("module")}>
                Back
              </Button>
              <Button onClick={() => setStep("mapping")} disabled={sourceType === "csv" && !file}>
                Next
              </Button>
            </div>
          </div>
        )}

        {step === "mapping" && (
          <div className="space-y-4">
            <Button size="sm" onClick={() => suggest.mutate()} disabled={!sourceFields.length}>
              Auto-suggest mappings
            </Button>
            <div className="grid gap-2 md:grid-cols-2">
              {(targetSchema?.result ?? []).map((t) => {
                const rule = rules.find((r) => r.targetField === t.field);
                return (
                  <label key={t.field} className="flex flex-col gap-1 text-sm">
                    {t.label}
                    {t.required && <span className="text-destructive">*</span>}
                    <Select
                      value={rule?.sourceField ?? ""}
                      onChange={(e) => {
                        const val = e.target.value;
                        setRules((prev) => {
                          const rest = prev.filter((r) => r.targetField !== t.field);
                          if (!val) return rest;
                          return [
                            ...rest,
                            { sourceField: val, targetField: t.field, isRequired: t.required },
                          ];
                        });
                      }}
                    >
                      <option value="">— unmapped —</option>
                      {sourceFields.map((sf) => (
                        <option key={sf} value={sf}>
                          {sf}
                        </option>
                      ))}
                    </Select>
                  </label>
                );
              })}
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setStep("upload")}>
                Back
              </Button>
              <Button onClick={() => setStep("preview")}>Preview</Button>
            </div>
          </div>
        )}

        {step === "preview" && (
          <div className="space-y-4">
            <Button size="sm" onClick={() => preview.mutate()} disabled={!sampleRows.length}>
              Run validation
            </Button>
            {preview.data?.result.summary && (
              <p className="text-sm">
                {preview.data.result.summary.valid ? (
                  <span className="text-status-success">All rows valid</span>
                ) : (
                  <span className="text-destructive">
                    {preview.data.result.summary.errorCount} errors,{" "}
                    {preview.data.result.summary.warningCount} warnings
                  </span>
                )}
              </p>
            )}
            {preview.data?.result.preview?.[0] && (
              <pre className="max-h-48 overflow-auto rounded-md border border-border bg-canvas p-2 text-xs text-fg">
                {JSON.stringify(preview.data.result.preview[0].transformed, null, 2)}
              </pre>
            )}
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => setStep("mapping")}>
                Back
              </Button>
              <Button onClick={() => startImport.mutate()} disabled={startImport.isPending}>
                Start import
              </Button>
            </div>
          </div>
        )}

        {step === "import" && runId && (
          <p className="text-sm">
            Import started. Run ID: <code>{runId}</code>. Track progress below.
          </p>
        )}
      </WizardShell>

      <section>
        <h2 className="mb-2 text-section font-semibold text-fg">Import runs</h2>
        <EnterpriseGrid<MigrationRun>
          columns={runColumns}
          rows={runs?.result ?? []}
          loading={isLoading}
          getRowId={(r) => r.id}
        />
      </section>
    </div>
  );
}
