"use client";

import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";

export type ProductCustomFieldDef = {
  fieldKey: string;
  label: string;
  fieldType: string;
  picklistOptions?: string[] | null;
};

type ProductCustomFieldsProps = {
  definitions: ProductCustomFieldDef[];
  values: Record<string, string>;
  onChange: (fieldKey: string, value: string) => void;
};

export function ProductCustomFields({
  definitions,
  values,
  onChange,
}: ProductCustomFieldsProps) {
  const productDefs = definitions.filter((d) => d.fieldKey);
  if (productDefs.length === 0) return null;

  return (
    <section className="space-y-4 rounded-lg border border-border bg-surface p-4">
      <h2 className="text-sm font-semibold text-fg">Custom fields</h2>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {productDefs.map((def) => {
          const value = values[def.fieldKey] ?? "";
          const label = def.label || def.fieldKey;
          if (def.fieldType === "picklist" && def.picklistOptions?.length) {
            return (
              <FormField key={def.fieldKey} label={label}>
                <Select
                  value={value}
                  onChange={(e) => onChange(def.fieldKey, e.target.value)}
                >
                  <option value="">—</option>
                  {def.picklistOptions.map((opt) => (
                    <option key={opt} value={opt}>
                      {opt}
                    </option>
                  ))}
                </Select>
              </FormField>
            );
          }
          return (
            <FormField key={def.fieldKey} label={label}>
              <Input
                inputMode={def.fieldType === "number" ? "decimal" : "text"}
                value={value}
                onChange={(e) => onChange(def.fieldKey, e.target.value)}
              />
            </FormField>
          );
        })}
      </div>
    </section>
  );
}

export function customFieldValuesToPayload(
  definitions: ProductCustomFieldDef[],
  values: Record<string, string>,
): Record<string, unknown> {
  const payload: Record<string, unknown> = {};
  for (const def of definitions) {
    const raw = values[def.fieldKey];
    if (raw === undefined || raw === "") continue;
    if (def.fieldType === "number") {
      const n = Number(raw);
      if (!Number.isNaN(n)) payload[def.fieldKey] = n;
    } else {
      payload[def.fieldKey] = raw;
    }
  }
  return payload;
}
