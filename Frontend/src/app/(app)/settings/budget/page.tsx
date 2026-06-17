"use client";
import { invalidateTenantQueries, useTenantReferenceQuery } from "@/lib/api/tenant-query";

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { EnterpriseGrid } from "@/components/ui/enterprise-grid";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { budgetsApi, type BudgetRow } from "@/lib/api/tenant";

import { responsiveListColumns } from "@/lib/grid/responsive-columns";

export default function BudgetSettingsPage() {
  const qc = useQueryClient();
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [fiscalYear, setFiscalYear] = useState(String(new Date().getFullYear()));
  const [nominalCode, setNominalCode] = useState("");
  const [lineAmount, setLineAmount] = useState("");

  const { data, isLoading, error } = useTenantReferenceQuery(["budgets"], () => budgetsApi.list());

  const create = useMutation({
    mutationFn: () =>
      budgetsApi.create({
        code,
        name,
        fiscalYear: Number(fiscalYear),
        lines:
          nominalCode && lineAmount ? [{ nominalCode, amount: lineAmount }] : [],
      }),
    onSuccess: () => {
      setCode("");
      setName("");
      setNominalCode("");
      setLineAmount("");
      void invalidateTenantQueries(qc, "budgets");
    },
  });

  const toggleActive = useMutation({
    mutationFn: ({ id, isActive }: { id: string; isActive: boolean }) =>
      budgetsApi.update(id, { isActive }),
    onSuccess: () => void invalidateTenantQueries(qc, "budgets"),
  });

  const columns = responsiveListColumns<BudgetRow>([
    { key: "code", header: "Code", sortable: true, sortAccessor: (r) => r.code },
    { key: "name", header: "Name", sortable: true, sortAccessor: (r) => r.name },
    {
      key: "fiscalYear",
      header: "Fiscal year",
      sortable: true,
      sortAccessor: (r) => r.fiscalYear,
    },
    {
      key: "lines",
      header: "Lines",
      render: (r) => String(r.lines?.length ?? 0),
    },
    {
      key: "isActive",
      header: "Active",
      render: (r) => (
        <Checkbox
          checked={r.isActive}
          onChange={(e) => {
            e.stopPropagation();
            toggleActive.mutate({ id: r.id, isActive: !r.isActive });
          }}
        />
      ),
    },
  ]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Budgets"
        description="Annual budgets by nominal code — FA §9.3."
      />

      <div className="grid max-w-3xl gap-3 md:grid-cols-2">
        <FormField label="Code">
          <Input value={code} onChange={(e) => setCode(e.target.value)} />
        </FormField>
        <FormField label="Name">
          <Input value={name} onChange={(e) => setName(e.target.value)} />
        </FormField>
        <FormField label="Fiscal year">
          <Input value={fiscalYear} onChange={(e) => setFiscalYear(e.target.value)} />
        </FormField>
        <FormField label="First nominal (optional)">
          <Input value={nominalCode} onChange={(e) => setNominalCode(e.target.value)} />
        </FormField>
        <FormField label="Amount (optional)">
          <Input value={lineAmount} onChange={(e) => setLineAmount(e.target.value)} />
        </FormField>
        <div className="flex items-end">
          <Button
            onClick={() => create.mutate()}
            disabled={create.isPending || !code || !name || !fiscalYear}
          >
            Add budget
          </Button>
        </div>
      </div>

      <EnterpriseGrid<BudgetRow>
        columns={columns}
        rows={data?.result ?? []}
        loading={isLoading}
        error={error}
        emptyMessage="No budgets yet."
        getRowId={(r) => r.id}
      />
    </div>
  );
}
