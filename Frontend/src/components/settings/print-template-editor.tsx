"use client";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import type { PrintTemplateSettings } from "@/lib/api/tenant";
import type { PrintTemplateMeta } from "@/config/print-template-catalog";

interface PrintTemplateEditorProps {
  meta: PrintTemplateMeta;
  value: PrintTemplateSettings;
  onChange: (next: PrintTemplateSettings) => void;
  onSave: () => void;
  saving?: boolean;
}

export function PrintTemplateEditor({
  meta,
  value,
  onChange,
  onSave,
  saving,
}: PrintTemplateEditorProps) {
  function patch(partial: Partial<PrintTemplateSettings>) {
    onChange({ ...value, ...partial });
  }

  return (
    <section className="max-w-2xl space-y-4 rounded-lg border border-border bg-surface p-6">
      <FormField label="Print title">
        <Input value={value.title} onChange={(e) => patch({ title: e.target.value })} />
      </FormField>

      <div className="grid gap-4 sm:grid-cols-2">
        <label className="flex items-center gap-2 text-sm">
          <Checkbox
            checked={value.showLogo}
            onChange={(e) => patch({ showLogo: e.target.checked })}
          />
          Show logo
        </label>
        <label className="flex items-center gap-2 text-sm">
          <Checkbox
            checked={value.showBusinessBlock}
            onChange={(e) => patch({ showBusinessBlock: e.target.checked })}
          />
          Show business block
        </label>
        <label className="flex items-center gap-2 text-sm">
          <Checkbox
            checked={value.showTaxColumns}
            onChange={(e) => patch({ showTaxColumns: e.target.checked })}
          />
          Show tax columns
        </label>
        {meta.supportsTwoCopies ? (
          <label className="flex items-center gap-2 text-sm">
            <Checkbox
              checked={Boolean(value.twoCopies)}
              onChange={(e) => patch({ twoCopies: e.target.checked })}
            />
            Two copies on one page
          </label>
        ) : null}
      </div>

      <FormField label="Paper size">
        <Select
          value={value.paperSize}
          onChange={(e) => patch({ paperSize: e.target.value as "A4" | "Letter" })}
        >
          <option value="A4">A4</option>
          <option value="Letter">Letter</option>
        </Select>
      </FormField>

      {meta.printModes && meta.printModes.length > 1 ? (
        <FormField label="Print mode">
          <Select
            value={value.printMode ?? meta.printModes[0]}
            onChange={(e) => patch({ printMode: e.target.value })}
          >
            {meta.printModes.map((m) => (
              <option key={m} value={m}>
                {m === "voucher" ? "Bank voucher" : "Journal layout"}
              </option>
            ))}
          </Select>
        </FormField>
      ) : null}

      <FormField label="Header note">
        <Input
          value={value.headerNote}
          onChange={(e) => patch({ headerNote: e.target.value })}
          placeholder="Optional text above document body"
        />
      </FormField>

      <FormField label="Footer note">
        <Input
          value={value.footerNote}
          onChange={(e) => patch({ footerNote: e.target.value })}
          placeholder="Optional footer / terms"
        />
      </FormField>

      <Button type="button" disabled={saving} onClick={onSave}>
        {saving ? "Saving…" : "Save template"}
      </Button>
    </section>
  );
}
