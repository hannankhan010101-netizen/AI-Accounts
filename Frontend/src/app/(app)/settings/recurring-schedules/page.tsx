/** Recurring document schedules — FA §3.3 */
"use client";

import { useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { invalidateTenantQueries, useTenantListQuery } from "@/lib/api/tenant-query";

import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";
import { PageHeader } from "@/components/ui/page-header";
import { Select } from "@/components/ui/select";
import { WorkspaceLoading } from "@/components/ui/workspace-loading";
import { useConfiguredListColumns } from "@/lib/hooks/use-configured-list-columns";
import {
  recurringSchedulesApi,
  type RecurringSchedule,
} from "@/lib/api/tenant";
import { ApiError } from "@/lib/api/client";
const MODULES = [
  { value: "sales_invoice", label: "Sales invoice (batch payload)" },
  { value: "supplier_bill", label: "Supplier bill (batch payload)" },
];

const FREQUENCIES = [
  { value: "daily", label: "Daily" },
  { value: "weekly", label: "Weekly" },
  { value: "monthly", label: "Monthly" },
];

type ScheduleRow = Record<string, unknown> & RecurringSchedule;

export default function RecurringSchedulesPage() {
  const qc = useQueryClient();
  const [showAdd, setShowAdd] = useState(false);
  const [name, setName] = useState("");
  const [module, setModule] = useState("sales_invoice");
  const [frequency, setFrequency] = useState("monthly");
  const [interval, setInterval] = useState("1");
  const [nextRunDate, setNextRunDate] = useState(new Date().toISOString().slice(0, 10));
  const [payloadJson, setPayloadJson] = useState(
    '{\n  "invoiceDate": "2026-01-01",\n  "entries": []\n}',
  );
  const [error, setError] = useState<string | null>(null);

  const { data, isLoading } = useTenantListQuery(["recurring-schedules"], () => recurringSchedulesApi.list());

  const rows = (data?.result ?? []) as ScheduleRow[];

  const baseColumns = useMemo(
    (): GridColumn<ScheduleRow>[] => [
      { key: "name", header: "Name", sortable: true, sortAccessor: (r) => r.name },
      { key: "module", header: "Module" },
      {
        key: "frequency",
        header: "Frequency",
        render: (r) => `${r.frequency} ×${r.interval}`,
      },
      {
        key: "nextRunDate",
        header: "Next run",
        render: (r) => new Date(r.nextRunDate).toLocaleDateString(),
      },
      {
        key: "isActive",
        header: "Active",
        render: (r) => (r.isActive ? "Yes" : "No"),
      },
    ],
    [],
  );
  const columns = useConfiguredListColumns("recurring-schedules", baseColumns);

  const createMutation = useMutation({
    mutationFn: () => {
      let payload: Record<string, unknown> = {};
      try {
        payload = JSON.parse(payloadJson) as Record<string, unknown>;
      } catch {
        throw new Error("Invalid JSON payload");
      }
      return recurringSchedulesApi.create({
        name: name.trim(),
        module,
        frequency,
        interval: Number(interval) || 1,
        nextRunDate: new Date(nextRunDate).toISOString(),
        payload,
      });
    },
    onSuccess: () => {
      setShowAdd(false);
      setError(null);
      setName("");
      void invalidateTenantQueries(qc, "recurring-schedules");
    },
    onError: (err) =>
      setError(err instanceof ApiError ? err.message : "Could not create schedule"),
  });

  const runDueMutation = useMutation({
    mutationFn: () => recurringSchedulesApi.runDue(),
    onSuccess: () => {
      void invalidateTenantQueries(qc, "recurring-schedules");
      void invalidateTenantQueries(qc, "sales-invoices");
      void invalidateTenantQueries(qc, "supplier-bills");
    },
  });

  const toggleMutation = useMutation({
    mutationFn: (row: RecurringSchedule) =>
      recurringSchedulesApi.update(row.id, { isActive: !row.isActive }),
    onSuccess: () => void invalidateTenantQueries(qc, "recurring-schedules"),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => recurringSchedulesApi.remove(id),
    onSuccess: () => void invalidateTenantQueries(qc, "recurring-schedules"),
  });

  return (
    <div>
      <PageHeader
        title="Recurring schedules"
        breadcrumb="Settings / Recurrence"
        description="Automate recurring sales invoices or supplier bills using batch payloads (§3.3)."
        actions={
          <>
            <Button
              type="button"
              variant="outline"
              disabled={runDueMutation.isPending}
              onClick={() => runDueMutation.mutate()}
            >
              {runDueMutation.isPending ? "Running…" : "Run due now"}
            </Button>
            <Button type="button" onClick={() => setShowAdd(true)}>
              Add schedule
            </Button>
          </>
        }
      />

      {isLoading ? (
        <WorkspaceLoading />
      ) : (
        <EnterpriseGrid<ScheduleRow>
          columns={[
            ...columns,
            {
              key: "actions",
              header: "",
              render: (r) => (
                <div className="flex gap-2">
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={() => toggleMutation.mutate(r)}
                  >
                    {r.isActive ? "Pause" : "Resume"}
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={() => deleteMutation.mutate(r.id)}
                  >
                    Delete
                  </Button>
                </div>
              ),
            },
          ]}
          rows={rows}
          layout="table"
          emptyMessage="No recurring schedules yet."
          getRowId={(r) => r.id}
        />
      )}

      <Modal
        open={showAdd}
        title="New recurring schedule"
        onClose={() => {
          setShowAdd(false);
          setError(null);
        }}
        footer={
          <>
            <Button type="button" variant="outline" onClick={() => setShowAdd(false)}>
              Cancel
            </Button>
            <Button
              type="button"
              disabled={!name.trim() || createMutation.isPending}
              onClick={() => createMutation.mutate()}
            >
              {createMutation.isPending ? "Saving…" : "Save"}
            </Button>
          </>
        }
      >
        <div className="grid gap-3">
          <FormField label="Name" required>
            <Input value={name} onChange={(e) => setName(e.target.value)} />
          </FormField>
          <FormField label="Module">
            <Select value={module} onChange={(e) => setModule(e.target.value)}>
              {MODULES.map((m) => (
                <option key={m.value} value={m.value}>
                  {m.label}
                </option>
              ))}
            </Select>
          </FormField>
          <div className="grid grid-cols-2 gap-3">
            <FormField label="Frequency">
              <Select value={frequency} onChange={(e) => setFrequency(e.target.value)}>
                {FREQUENCIES.map((f) => (
                  <option key={f.value} value={f.value}>
                    {f.label}
                  </option>
                ))}
              </Select>
            </FormField>
            <FormField label="Interval">
              <Input
                type="number"
                min={1}
                value={interval}
                onChange={(e) => setInterval(e.target.value)}
              />
            </FormField>
          </div>
          <FormField label="Next run date">
            <Input
              type="date"
              value={nextRunDate}
              onChange={(e) => setNextRunDate(e.target.value)}
            />
          </FormField>
          <FormField label="Payload (JSON — batch create body)">
            <textarea
              className="min-h-[160px] w-full rounded-md border border-border bg-canvas px-3 py-2 font-mono text-xs"
              value={payloadJson}
              onChange={(e) => setPayloadJson(e.target.value)}
            />
          </FormField>
          {error ? <p className="text-sm text-status-danger">{error}</p> : null}
        </div>
      </Modal>
    </div>
  );
}
