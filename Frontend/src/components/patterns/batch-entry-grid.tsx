"use client";

import { Plus, Trash2 } from "lucide-react";
import type { FieldArrayPath, UseFieldArrayReturn, UseFormReturn } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import type { Product } from "@/lib/api/tenant";

export interface BatchEntryRow {
  partyId: string;
  productCode?: string;
  quantity: string;
  rate: string;
  gstRate?: string;
  gstCode?: string;
}

interface PartyOption {
  id: string;
  label: string;
}

interface BatchEntryGridProps<T extends { entries: BatchEntryRow[] }> {
  form: UseFormReturn<T>;
  entries: UseFieldArrayReturn<T, FieldArrayPath<T> & "entries">;
  partyLabel: string;
  parties: PartyOption[];
  products: Product[] | undefined;
  gstRates: { taxCode?: string | null; taxRate?: number | string | null }[];
  emptyRow: () => BatchEntryRow;
}

export function BatchEntryGrid<T extends { entries: BatchEntryRow[] }>({
  form,
  entries,
  partyLabel,
  parties,
  products,
  gstRates,
  emptyRow,
}: BatchEntryGridProps<T>) {
  return (
    <div>
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-fg">Batch lines</h2>
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => entries.append(emptyRow() as never)}
        >
          <Plus className="mr-1 h-4 w-4" aria-hidden />
          Add row
        </Button>
      </div>
      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-fg-muted">
              <th className="py-2 pl-3 pr-3">{partyLabel}</th>
              <th className="py-2 pr-3">Product</th>
              <th className="py-2 pr-3 text-right">Qty</th>
              <th className="py-2 pr-3 text-right">Rate</th>
              <th className="py-2 pr-3">GST %</th>
              <th className="w-10 py-2" />
            </tr>
          </thead>
          <tbody>
            {entries.fields.map((field, i) => (
              <tr key={field.id} className="border-b border-border">
                <td className="py-1 pl-3 pr-3">
                  <Select className="h-8 min-w-[10rem]" {...form.register(`entries.${i}.partyId` as never)}>
                    <option value="">Select…</option>
                    {parties.map((p) => (
                      <option key={p.id} value={p.id}>
                        {p.label}
                      </option>
                    ))}
                  </Select>
                </td>
                <td className="py-1 pr-3">
                  <Select className="h-8 min-w-[8rem]" {...form.register(`entries.${i}.productCode` as never)}>
                    <option value="">—</option>
                    {products?.map((p) => (
                      <option key={p.id} value={p.code ?? ""}>
                        {p.code ? `${p.code} — ` : ""}
                        {p.name}
                      </option>
                    ))}
                  </Select>
                </td>
                <td className="py-1 pr-3">
                  <Input
                    inputMode="decimal"
                    className="h-8 w-24 text-right"
                    {...form.register(`entries.${i}.quantity` as never)}
                  />
                </td>
                <td className="py-1 pr-3">
                  <Input
                    inputMode="decimal"
                    className="h-8 w-28 text-right"
                    {...form.register(`entries.${i}.rate` as never)}
                  />
                </td>
                <td className="py-1 pr-3">
                  <Select
                    className="h-8 w-28"
                    {...form.register(`entries.${i}.gstRate` as never)}
                    onChange={(e) => {
                      const val = e.target.value;
                      form.setValue(`entries.${i}.gstRate` as never, val as never);
                      const match = gstRates.find((g) => String(g.taxRate ?? 0) === val);
                      if (match?.taxCode) {
                        form.setValue(`entries.${i}.gstCode` as never, match.taxCode as never);
                      }
                    }}
                  >
                    <option value="">0</option>
                    {gstRates.map((g, gi) => (
                      <option key={gi} value={String(g.taxRate ?? 0)}>
                        {g.taxCode ? `${g.taxCode} ` : ""}
                        {g.taxRate ?? 0}%
                      </option>
                    ))}
                  </Select>
                </td>
                <td className="py-1">
                  <button
                    type="button"
                    onClick={() => entries.remove(i)}
                    disabled={entries.fields.length <= 1}
                    aria-label="Remove row"
                    className="rounded p-1 text-fg-muted hover:bg-status-danger/10 hover:text-status-danger disabled:opacity-30"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-2 text-xs text-fg-muted">
        Rows are grouped by {partyLabel.toLowerCase()} on save — one draft document per party.
      </p>
    </div>
  );
}
