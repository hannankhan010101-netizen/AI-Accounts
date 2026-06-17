"use client";

import { Trash2, Plus } from "lucide-react";
import type { UseFormRegister } from "react-hook-form";

import type { TaxesYearEndFormShape } from "@/lib/settings/taxes-year-end-form";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { Input } from "@/components/ui/input";
import type { TaxRateRow, TaxRegion, WhtRow } from "@/lib/api/tenant";

type IndexedRow = { _index: number; _fieldId: string };

export function TaxDisplayGrid({
  rows,
  register,
}: {
  rows: { key: string; description: string }[];
  register: UseFormRegister<TaxesYearEndFormShape>;
}) {
  const columns: GridColumn<{ key: string; description: string }>[] = [
    { key: "description", header: "Description" },
    {
      key: "label",
      header: "Label",
      render: (r) => (
        <Input className="h-8" {...register(`taxDisplay.${r.key}.label` as const)} />
      ),
    },
    {
      key: "supplier",
      header: "Supplier",
      render: (r) => <Checkbox {...register(`taxDisplay.${r.key}.supplier` as const)} />,
    },
    {
      key: "customer",
      header: "Customer",
      render: (r) => <Checkbox {...register(`taxDisplay.${r.key}.customer` as const)} />,
    },
  ];

  return (
    <EnterpriseGrid
      columns={columns}
      rows={rows}
      layout="table"
      emptyMessage="No tax display rows."
      getRowId={(r) => r.key}
    />
  );
}

export function TaxRateGrid({
  title,
  fields,
  namePrefix,
  register,
  onAdd,
  onRemove,
}: {
  title: string;
  fields: { id: string }[];
  namePrefix: "gstRates" | "adtRates" | "fedRates";
  register: UseFormRegister<TaxesYearEndFormShape>;
  onAdd: () => void;
  onRemove: (i: number) => void;
}) {
  const rows: (TaxRateRow & IndexedRow)[] = fields.map((f, i) => ({
    _index: i,
    _fieldId: f.id,
    region: "",
    regionCode: "",
    taxCode: "",
  }));

  const columns: GridColumn<TaxRateRow & IndexedRow>[] = [
    {
      key: "region",
      header: "Region",
      render: (r) => (
        <Input className="h-8 min-w-[6rem]" {...register(`${namePrefix}.${r._index}.region` as const)} />
      ),
    },
    {
      key: "regionCode",
      header: "Region code",
      render: (r) => (
        <Input
          className="h-8 min-w-[5rem]"
          {...register(`${namePrefix}.${r._index}.regionCode` as const)}
        />
      ),
    },
    {
      key: "taxCode",
      header: "Tax code",
      render: (r) => (
        <Input className="h-8 min-w-[5rem]" {...register(`${namePrefix}.${r._index}.taxCode` as const)} />
      ),
    },
    {
      key: "taxRate",
      header: "Rate %",
      align: "right",
      render: (r) => (
        <Input
          type="number"
          step="0.01"
          className="h-8 w-20 text-right"
          {...register(`${namePrefix}.${r._index}.taxRate` as const, { valueAsNumber: true })}
        />
      ),
    },
    {
      key: "additionalTaxRate",
      header: "Add. %",
      align: "right",
      render: (r) => (
        <Input
          type="number"
          step="0.01"
          className="h-8 w-20 text-right"
          {...register(`${namePrefix}.${r._index}.additionalTaxRate` as const, {
            valueAsNumber: true,
          })}
        />
      ),
    },
    {
      key: "accountId",
      header: "Account",
      render: (r) => (
        <Input className="h-8 min-w-[5rem]" {...register(`${namePrefix}.${r._index}.accountId` as const)} />
      ),
    },
    {
      key: "printLabel",
      header: "Print label",
      render: (r) => (
        <Input className="h-8 min-w-[5rem]" {...register(`${namePrefix}.${r._index}.printLabel` as const)} />
      ),
    },
    {
      key: "status",
      header: "Status",
      render: (r) => (
        <Input className="h-8 w-24" {...register(`${namePrefix}.${r._index}.status` as const)} />
      ),
    },
    {
      key: "actions",
      header: "",
      render: (r) => (
        <button
          type="button"
          onClick={() => onRemove(r._index)}
          aria-label="Remove rate row"
          className="rounded p-1 text-fg-muted hover:bg-status-danger/10 hover:text-status-danger"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      ),
    },
  ];

  return (
    <section className="rounded-lg border border-border bg-surface p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-fg">{title}</h2>
        <Button type="button" size="sm" variant="outline" onClick={onAdd}>
          <Plus className="mr-1 h-4 w-4" /> Add row
        </Button>
      </div>
      <EnterpriseGrid
        columns={columns}
        rows={rows}
        layout="table"
        emptyMessage="No rates defined. Click Add row."
        getRowId={(r) => r._fieldId}
      />
    </section>
  );
}

export function WhtRateGrid({
  fields,
  register,
  onAdd,
  onRemove,
}: {
  fields: { id: string }[];
  register: UseFormRegister<TaxesYearEndFormShape>;
  onAdd: () => void;
  onRemove: (i: number) => void;
}) {
  const rows: (WhtRow & IndexedRow)[] = fields.map((f, i) => ({
    _index: i,
    _fieldId: f.id,
  }));

  const columns: GridColumn<WhtRow & IndexedRow>[] = [
    {
      key: "taxName",
      header: "Tax name",
      render: (r) => (
        <Input className="h-8" {...register(`whtRates.${r._index}.taxName` as const)} />
      ),
    },
    {
      key: "taxCode",
      header: "Tax code",
      render: (r) => (
        <Input className="h-8" {...register(`whtRates.${r._index}.taxCode` as const)} />
      ),
    },
    {
      key: "taxRate",
      header: "Rate %",
      align: "right",
      render: (r) => (
        <Input
          type="number"
          step="0.01"
          className="h-8 w-24 text-right"
          {...register(`whtRates.${r._index}.taxRate` as const, { valueAsNumber: true })}
        />
      ),
    },
    {
      key: "actions",
      header: "",
      render: (r) => (
        <button
          type="button"
          onClick={() => onRemove(r._index)}
          aria-label="Remove WHT row"
          className="rounded p-1 text-fg-muted hover:bg-status-danger/10 hover:text-status-danger"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      ),
    },
  ];

  return (
    <section className="rounded-lg border border-border bg-surface p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-fg">WHT rates</h2>
        <Button type="button" size="sm" variant="outline" onClick={onAdd}>
          <Plus className="mr-1 h-4 w-4" /> Add row
        </Button>
      </div>
      <EnterpriseGrid
        columns={columns}
        rows={rows}
        layout="table"
        emptyMessage="No WHT rates. Click Add row."
        getRowId={(r) => r._fieldId}
      />
    </section>
  );
}

export function TaxRegionGrid({
  fields,
  register,
  onAdd,
  onRemove,
}: {
  fields: { id: string }[];
  register: UseFormRegister<TaxesYearEndFormShape>;
  onAdd: () => void;
  onRemove: (i: number) => void;
}) {
  const rows: (TaxRegion & IndexedRow)[] = fields.map((f, i) => ({
    _index: i,
    _fieldId: f.id,
  }));

  const columns: GridColumn<TaxRegion & IndexedRow>[] = [
    {
      key: "regionName",
      header: "Region name",
      render: (r) => (
        <Input className="h-8" {...register(`taxRegions.${r._index}.regionName` as const)} />
      ),
    },
    {
      key: "regionCode",
      header: "Region code",
      render: (r) => (
        <Input className="h-8" {...register(`taxRegions.${r._index}.regionCode` as const)} />
      ),
    },
    {
      key: "actions",
      header: "",
      render: (r) => (
        <button
          type="button"
          onClick={() => onRemove(r._index)}
          aria-label="Remove region"
          className="rounded p-1 text-fg-muted hover:bg-status-danger/10 hover:text-status-danger"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      ),
    },
  ];

  return (
    <section className="rounded-lg border border-border bg-surface p-4">
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-fg">Tax regions</h2>
        <Button type="button" size="sm" variant="outline" onClick={onAdd}>
          <Plus className="mr-1 h-4 w-4" /> Add row
        </Button>
      </div>
      <EnterpriseGrid
        columns={columns}
        rows={rows}
        layout="table"
        emptyMessage="No regions defined."
        getRowId={(r) => r._fieldId}
      />
    </section>
  );
}
