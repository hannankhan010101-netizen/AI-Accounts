"use client";

import { Plus, Trash2 } from "lucide-react";
import type { FieldArrayWithId, UseFieldArrayReturn, UseFormReturn } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import type { Product } from "@/lib/api/tenant";

export type ProductLineField =
  | { kind: "product"; name: string; label?: string }
  | {
      kind: "text";
      name: string;
      label: string;
      align?: "left" | "right";
      placeholder?: string;
      inputMode?: "decimal" | "text";
      widthClass?: string;
    };

interface ProductLinesEditorProps {
  form: UseFormReturn<any>;
  lines: UseFieldArrayReturn<any, "lines", "id">;
  products?: Product[];
  fields: ProductLineField[];
  emptyLine: () => Record<string, string>;
  productOptional?: boolean;
}

export function ProductLinesEditor({
  form,
  lines,
  products = [],
  fields,
  emptyLine,
  productOptional = false,
}: ProductLinesEditorProps) {
  const register = form.register;

  return (
    <div>
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-fg">Lines</h2>
        <Button type="button" variant="outline" size="sm" onClick={() => lines.append(emptyLine())}>
          <Plus className="mr-1 h-4 w-4" /> Add line
        </Button>
      </div>
      <div className="overflow-x-auto rounded-lg border border-border bg-surface">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-fg-muted">
              {fields.map((f) => (
                <th
                  key={f.name}
                  className={`px-3 py-2 ${f.kind === "text" && f.align === "right" ? "text-right" : ""}`}
                >
                  {f.kind === "product" ? f.label ?? "Product" : f.label}
                </th>
              ))}
              <th className="w-10 px-3 py-2" aria-label="Actions" />
            </tr>
          </thead>
          <tbody>
            {lines.fields.map((field: FieldArrayWithId, i: number) => (
              <tr key={field.id} className="border-b border-border/60 last:border-b-0">
                {fields.map((col) => (
                  <td key={col.name} className="px-3 py-1.5">
                    {col.kind === "product" ? (
                      <Select className="h-8" {...register(`lines.${i}.${col.name}` as const)}>
                        {productOptional ? <option value="">—</option> : <option value="">Select…</option>}
                        {products.map((p) => (
                          <option key={p.id} value={p.code ?? ""}>
                            {p.code} — {p.name}
                          </option>
                        ))}
                      </Select>
                    ) : (
                      <Input
                        inputMode={col.inputMode}
                        placeholder={col.placeholder}
                        className={`h-8 ${col.widthClass ?? ""} ${col.align === "right" ? "text-right tabular-nums" : ""}`}
                        {...register(`lines.${i}.${col.name}` as const)}
                      />
                    )}
                  </td>
                ))}
                <td className="px-3 py-1.5">
                  <button
                    type="button"
                    onClick={() => lines.remove(i)}
                    disabled={lines.fields.length <= 1}
                    className="rounded p-1 text-fg-muted hover:bg-status-danger/10 hover:text-status-danger disabled:opacity-30"
                    aria-label="Remove line"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
