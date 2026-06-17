"use client";

import type { FieldArrayPath, UseFieldArrayReturn, UseFormReturn } from "react-hook-form";
import { Plus, Trash2 } from "lucide-react";
import { useCallback, useMemo, useState } from "react";
import Decimal from "decimal.js";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { inventoryWritesApi, type Product, type ProductBatch } from "@/lib/api/tenant";
import type { ProductDescriptionColumn } from "@/lib/hooks/product-description-columns";

export interface GstLineRow {
  productCode?: string;
  quantity: string;
  rate: string;
  gstCode?: string;
  gstRate?: string;
  adtCode?: string;
  fedCode?: string;
  projectCode?: string;
  description?: string;
  text1?: string;
  text2?: string;
  text3?: string;
  text4?: string;
  text5?: string;
  text6?: string;
  batchNumber?: string;
  expiryDate?: string;
}

export interface GstRateOption {
  taxCode?: string | null;
  taxRate?: number | string | null;
}

interface GstLineGridProps<T extends { lines: GstLineRow[] }> {
  form: UseFormReturn<T>;
  lines: UseFieldArrayReturn<T, FieldArrayPath<T> & "lines">;
  lineTotals: Decimal[];
  products: Product[] | undefined;
  gstRates: GstRateOption[];
  adtRates?: GstRateOption[];
  fedRates?: GstRateOption[];
  showProject?: boolean;
  emptyLine: () => GstLineRow;
  /** Workflow tour anchor on the lines block. */
  tourTarget?: string;
  onProductSelect?: (index: number, productCode: string) => void;
  descriptionColumns?: ProductDescriptionColumn[];
  /** FA §7.8 — pick batch/expiry per line when product has batches. */
  showBatchExpiry?: boolean;
}

function dec(value: string): Decimal {
  if (!value) return new Decimal(0);
  try {
    return new Decimal(value);
  } catch {
    return new Decimal(0);
  }
}

export function GstLineGrid<T extends { lines: GstLineRow[] }>({
  form,
  lines,
  lineTotals,
  products,
  gstRates,
  adtRates = [],
  fedRates = [],
  showProject = true,
  emptyLine,
  tourTarget,
  onProductSelect,
  descriptionColumns = [],
  showBatchExpiry = false,
}: GstLineGridProps<T>) {
  const [batchesByLine, setBatchesByLine] = useState<Record<number, ProductBatch[]>>({});

  const loadBatches = useCallback(async (lineIndex: number, productCode: string) => {
    if (!showBatchExpiry || !productCode) {
      setBatchesByLine((prev) => {
        const next = { ...prev };
        delete next[lineIndex];
        return next;
      });
      return;
    }
    try {
      const res = await inventoryWritesApi.listBatches(productCode);
      setBatchesByLine((prev) => ({ ...prev, [lineIndex]: res.result ?? [] }));
    } catch {
      setBatchesByLine((prev) => ({ ...prev, [lineIndex]: [] }));
    }
  }, [showBatchExpiry]);

  const grandTotal = useMemo(
    () => lineTotals.reduce((acc, total) => acc.plus(total), new Decimal(0)),
    [lineTotals],
  );

  const onBatchSelect = useCallback(
    (lineIndex: number, batchNumber: string, options: ProductBatch[]) => {
      form.setValue(`lines.${lineIndex}.batchNumber` as never, batchNumber as never);
      const match = options.find((b) => b.batchNumber === batchNumber);
      if (match?.expiryDate) {
        form.setValue(
          `lines.${lineIndex}.expiryDate` as never,
          match.expiryDate.slice(0, 10) as never,
        );
      }
    },
    [form],
  );

  return (
    <div {...(tourTarget ? { "data-tour": tourTarget } : {})}>
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-fg">Lines</h2>
        <Button type="button" variant="outline" size="sm" onClick={() => lines.append(emptyLine() as never)}>
          <Plus className="mr-1 h-4 w-4" aria-hidden />
          Add line
        </Button>
      </div>
      <div className="relative overflow-x-auto scrollbar-gutter-stable rounded-lg border border-border">
        <p className="pointer-events-none px-3 pt-2 text-[10px] text-fg-muted md:hidden">
          Swipe for more columns →
        </p>
        <table className="min-w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-fg-muted">
              <th className="sticky left-0 z-10 bg-surface py-2 pr-3">Product</th>
              {descriptionColumns.map((col) => (
                <th
                  key={col.fieldKey}
                  className="py-2 pr-3"
                  style={col.width ? { minWidth: col.width } : undefined}
                >
                  {col.header}
                </th>
              ))}
              <th className="py-2 pr-3 text-right">Qty</th>
              <th className="py-2 pr-3 text-right">Rate</th>
              <th className="py-2 pr-3">GST %</th>
              {adtRates.length > 0 ? <th className="py-2 pr-3">ADT</th> : null}
              {fedRates.length > 0 ? <th className="py-2 pr-3">FED</th> : null}
              {showBatchExpiry ? (
                <>
                  <th className="py-2 pr-3">Batch</th>
                  <th className="py-2 pr-3">Expiry</th>
                </>
              ) : null}
              <th className="py-2 pr-3 text-right">Line total</th>
              {showProject && <th className="py-2 pr-3">Project</th>}
              <th className="py-2 w-10" />
            </tr>
          </thead>
          <tbody>
            {lines.fields.map((field, i) => (
              <tr
                key={field.id}
                className={cn(
                  "border-b border-border",
                  i % 2 === 1 && "bg-canvas/50 dark:bg-canvas/20",
                )}
              >
                <td className={cn("sticky left-0 z-[1] py-1 pr-3", i % 2 === 1 ? "bg-canvas/50 dark:bg-canvas/20" : "bg-surface")}>
                  <Select
                    className="h-8 min-w-[8rem] max-md:h-11 max-md:text-base"
                    {...form.register(`lines.${i}.productCode` as never)}
                    onChange={(e) => {
                      const val = e.target.value;
                      form.setValue(`lines.${i}.productCode` as never, val as never);
                      if (val) {
                        onProductSelect?.(i, val);
                        void loadBatches(i, val);
                        const product = products?.find((p) => p.code === val);
                        for (const col of descriptionColumns) {
                          if (col.fillFromProductName && product?.name) {
                            form.setValue(
                              `lines.${i}.${col.fieldKey}` as never,
                              product.name as never,
                            );
                          }
                        }
                      }
                    }}
                  >
                    <option value="">— No product —</option>
                    {products?.map((p) => (
                      <option key={p.id} value={p.code ?? ""}>
                        {p.code ? `${p.code} — ` : ""}
                        {p.name}
                      </option>
                    ))}
                  </Select>
                </td>
                {descriptionColumns.map((col) => (
                  <td key={col.fieldKey} className="py-1 pr-3">
                    <Input
                      className="h-8 min-w-[6rem]"
                      style={col.width ? { width: col.width } : undefined}
                      {...form.register(`lines.${i}.${col.fieldKey}` as never)}
                    />
                  </td>
                ))}
                <td className="py-1 pr-3">
                  <Input
                    inputMode="decimal"
                    className="h-8 w-24 text-right tabular-nums"
                    {...form.register(`lines.${i}.quantity` as never)}
                  />
                </td>
                <td className="py-1 pr-3">
                  <Input
                    inputMode="decimal"
                    className="h-8 w-28 text-right tabular-nums"
                    {...form.register(`lines.${i}.rate` as never)}
                  />
                </td>
                <td className="py-1 pr-3">
                  <Select
                    className="h-8 w-28"
                    {...form.register(`lines.${i}.gstRate` as never)}
                    onChange={(e) => {
                      const val = e.target.value;
                      form.setValue(`lines.${i}.gstRate` as never, val as never);
                      const match = gstRates.find((g) => String(g.taxRate ?? 0) === val);
                      if (match?.taxCode) {
                        form.setValue(`lines.${i}.gstCode` as never, match.taxCode as never);
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
                {adtRates.length > 0 ? (
                  <td className="py-1 pr-3">
                    <Select className="h-8 w-28" {...form.register(`lines.${i}.adtCode` as never)}>
                      <option value="">—</option>
                      {adtRates.map((g, gi) => (
                        <option key={gi} value={String(g.taxCode ?? "")}>
                          {g.taxCode} {g.taxRate ?? 0}%
                        </option>
                      ))}
                    </Select>
                  </td>
                ) : null}
                {fedRates.length > 0 ? (
                  <td className="py-1 pr-3">
                    <Select className="h-8 w-28" {...form.register(`lines.${i}.fedCode` as never)}>
                      <option value="">—</option>
                      {fedRates.map((g, gi) => (
                        <option key={gi} value={String(g.taxCode ?? "")}>
                          {g.taxCode} {g.taxRate ?? 0}%
                        </option>
                      ))}
                    </Select>
                  </td>
                ) : null}
                {showBatchExpiry ? (
                  <>
                    <td className="py-1 pr-3">
                      <Select
                        className="h-8 min-w-[7rem]"
                        {...form.register(`lines.${i}.batchNumber` as never)}
                        onChange={(e) => {
                          const val = e.target.value;
                          onBatchSelect(i, val, batchesByLine[i] ?? []);
                        }}
                      >
                        <option value="">—</option>
                        {(batchesByLine[i] ?? []).map((b) => (
                          <option key={b.id} value={b.batchNumber}>
                            {b.batchNumber}
                            {b.quantityOnHand != null ? ` (${b.quantityOnHand})` : ""}
                          </option>
                        ))}
                      </Select>
                    </td>
                    <td className="py-1 pr-3">
                      <Input
                        type="date"
                        className="h-8 w-36"
                        {...form.register(`lines.${i}.expiryDate` as never)}
                      />
                    </td>
                  </>
                ) : null}
                <td className="py-1 pr-3 text-right tabular-nums">
                  {lineTotals[i]?.toFixed(2) ?? dec("0").toFixed(2)}
                </td>
                {showProject && (
                  <td className="py-1 pr-3">
                    <Input className="h-8 w-28" {...form.register(`lines.${i}.projectCode` as never)} />
                  </td>
                )}
                <td className="py-1">
                  <button
                    type="button"
                    onClick={() => lines.remove(i)}
                    disabled={lines.fields.length <= 1}
                    aria-label="Remove line"
                    className="rounded p-1 text-fg-muted hover:bg-status-danger/10 hover:text-status-danger disabled:cursor-not-allowed disabled:opacity-30"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr className="sticky bottom-0 border-t-2 border-border bg-surface">
              <td colSpan={100} className="py-2.5 px-3 text-right text-xs font-semibold uppercase tracking-wide text-fg-muted">
                {lines.fields.length} {lines.fields.length === 1 ? "line" : "lines"} · Total{" "}
                <span className="tabular-nums text-fg">{grandTotal.toFixed(2)}</span>
              </td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
}
