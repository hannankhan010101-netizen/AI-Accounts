"use client";

import { Plus, Trash2 } from "lucide-react";
import type { UseFieldArrayReturn, UseFormReturn } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface JournalLinesEditorProps {
  form: UseFormReturn<any>;
  lines: UseFieldArrayReturn<any, "lines", "id">;
  emptyLine: () => Record<string, string>;
  minLines?: number;
  tourTarget?: string;
}

export function JournalLinesEditor({
  form,
  lines,
  emptyLine,
  minLines = 2,
  tourTarget,
}: JournalLinesEditorProps) {
  const register = form.register;

  return (
    <div {...(tourTarget ? { "data-tour": tourTarget } : {})}>
      <div className="mb-3 flex items-center justify-between">
        <h2 className="text-sm font-semibold text-fg">Journal lines</h2>
        <Button type="button" variant="outline" size="sm" onClick={() => lines.append(emptyLine())}>
          <Plus className="mr-1 h-4 w-4" /> Add line
        </Button>
      </div>
      <div className="overflow-x-auto rounded-lg border border-border bg-surface">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="border-b border-border text-left text-xs uppercase tracking-wide text-fg-muted">
              <th className="px-3 py-2">Nominal code</th>
              <th className="px-3 py-2 text-right">Debit</th>
              <th className="px-3 py-2 text-right">Credit</th>
              <th className="px-3 py-2">Project</th>
              <th className="w-10 px-3 py-2" aria-label="Actions" />
            </tr>
          </thead>
          <tbody>
            {lines.fields.map((field, i) => (
              <tr key={field.id} className="border-b border-border/60 last:border-b-0">
                <td className="px-3 py-1.5">
                  <Input className="h-8 font-mono" {...register(`lines.${i}.nominalCode` as const)} />
                </td>
                <td className="px-3 py-1.5">
                  <Input
                    inputMode="decimal"
                    className="h-8 w-32 text-right tabular-nums"
                    {...register(`lines.${i}.debit` as const)}
                  />
                </td>
                <td className="px-3 py-1.5">
                  <Input
                    inputMode="decimal"
                    className="h-8 w-32 text-right tabular-nums"
                    {...register(`lines.${i}.credit` as const)}
                  />
                </td>
                <td className="px-3 py-1.5">
                  <Input className="h-8 w-32" {...register(`lines.${i}.projectCode` as const)} />
                </td>
                <td className="px-3 py-1.5">
                  <button
                    type="button"
                    onClick={() => lines.remove(i)}
                    disabled={lines.fields.length <= minLines}
                    aria-label="Remove line"
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
      {form.formState.errors.lines?.message ? (
        <p className="mt-2 text-xs text-status-danger">
          {String(form.formState.errors.lines.message)}
        </p>
      ) : null}
    </div>
  );
}
