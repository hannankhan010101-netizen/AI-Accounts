"use client";

import type { ReactNode } from "react";
import { useFieldArray, type UseFormReturn } from "react-hook-form";

import { AccordionItem } from "@/components/ui/accordion";
import { Checkbox } from "@/components/ui/checkbox";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export interface SmartSettingsPayload {
  others?: Record<string, boolean | string>;
  currency?: {
    baseCurrency?: string;
    timeZone?: string;
    dateFormat?: string;
  };
  defaults?: {
    receivablesNominalCode?: string;
    salesNominalCode?: string;
    payablesNominalCode?: string;
    purchasesNominalCode?: string;
  };
  sales?: ModuleSmartConfig;
  purchases?: ModuleSmartConfig;
  bank?: ModuleSmartConfig;
  fixedAssets?: ModuleSmartConfig;
  eSignatures?: ESignatureRow[];
  productDescription?: ProductDescriptionRow[];
  templateDraft?: Record<string, boolean>;
  lastRate?: Record<string, { addEdit?: boolean; view?: boolean }>;
  autoCodes?: Record<string, AutoCodeConfig>;
}

interface ModuleSmartConfig {
  smartFilters?: Record<string, string>;
  smartDocs?: Record<string, string>;
  notes?: Record<string, string>;
}

interface ESignatureRow {
  id?: string;
  name?: string;
  signatureUrl?: string;
}

interface ProductDescriptionRow {
  displayName?: string;
  label?: string;
  width?: string;
  transactionTypes?: string;
}

interface AutoCodeConfig {
  enabled?: boolean;
  prefix?: string;
  startSerial?: string;
}

const FILTER_KEYS = ["filter1", "filter2", "filter3", "filter4"] as const;
const DOC_KEYS = ["doc1", "doc2", "doc3", "doc4"] as const;

const AUTO_CODE_ENTITIES = [
  ["customer", "Customer Auto Account No."],
  ["supplier", "Supplier Auto Account No."],
  ["product", "Product Auto Code"],
  ["location", "Location Auto Code"],
  ["project", "Project Auto Code"],
  ["wht", "WHT Auto Code"],
  ["gst", "GST Auto Code"],
  ["adt", "ADT Auto Code"],
  ["fed", "FED Auto Code"],
  ["nominal", "Nominal Auto Code"],
] as const;

const TEMPLATE_DRAFT_MODULES = [
  ["journal", "Journal"],
  ["bankPayment", "Bank payments"],
  ["bankReceipt", "Bank receipts"],
  ["bankTransfer", "Bank transfers"],
  ["bills", "Bills"],
  ["grn", "GRN"],
  ["gdn", "GDN"],
  ["saleInvoices", "Sale invoices"],
  ["saleReceipts", "Sale receipts"],
  ["supplierPayments", "Supplier payments"],
] as const;

const LAST_RATE_TYPES = ["PO", "QO", "SC", "SI", "SO", "VC", "VI"] as const;

function SmartFilterFields({
  form,
  prefix,
  includeDocs = true,
}: {
  form: UseFormReturn<SmartSettingsPayload>;
  prefix: "sales" | "purchases" | "bank" | "fixedAssets";
  includeDocs?: boolean;
}) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {FILTER_KEYS.map((key, i) => (
          <FormField key={key} label={`Smart Filter ${i + 1}`}>
            <Input
              placeholder={`Filter ${i + 1} label`}
              {...form.register(`${prefix}.smartFilters.${key}` as const)}
            />
          </FormField>
        ))}
      </div>
      {includeDocs ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {DOC_KEYS.map((key, i) => (
            <FormField key={key} label={`Smart Doc ${i + 1}`}>
              <Input
                placeholder={`Doc ${i + 1} label`}
                {...form.register(`${prefix}.smartDocs.${key}` as const)}
              />
            </FormField>
          ))}
        </div>
      ) : null}
    </div>
  );
}

function NotesFields({
  form,
  fields,
}: {
  form: UseFormReturn<SmartSettingsPayload>;
  fields: readonly [string, string][];
}) {
  return (
    <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2">
      {fields.map(([key, label]) => (
        <FormField key={key} label={label}>
          <Input {...form.register(`sales.notes.${key}` as const)} />
        </FormField>
      ))}
    </div>
  );
}

function AutoCodeBlock({
  form,
  entityKey,
  title,
}: {
  form: UseFormReturn<SmartSettingsPayload>;
  entityKey: string;
  title: string;
}) {
  const base = `autoCodes.${entityKey}` as const;
  return (
    <AccordionItem key={title} title={title}>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <label className="flex items-center gap-2 text-sm text-fg">
          <Checkbox {...form.register(`${base}.enabled` as const)} />
          Enable auto code
        </label>
        <FormField label="Prefix">
          <Input {...form.register(`${base}.prefix` as const)} />
        </FormField>
        <FormField label="Auto start serial number">
          <Input {...form.register(`${base}.startSerial` as const)} />
        </FormField>
      </div>
    </AccordionItem>
  );
}

export function renderSmartSettingsSection(
  title: string,
  form: UseFormReturn<SmartSettingsPayload>,
): ReactNode {
  if (title === "Sales") {
    return (
      <AccordionItem key={title} title={title}>
        <SmartFilterFields form={form} prefix="sales" />
        <NotesFields
          form={form}
          fields={[
            ["salesInvoice", "Sales invoice notes"],
            ["salesOrder", "Sales order notes"],
            ["gdn", "GDN notes"],
            ["quotation", "Quotations notes"],
          ]}
        />
      </AccordionItem>
    );
  }

  if (title === "Purchases") {
    return (
      <AccordionItem key={title} title={title}>
        <SmartFilterFields form={form} prefix="purchases" />
        <div className="mt-4">
          <FormField label="Purchase order notes">
            <Input {...form.register("purchases.notes.purchaseOrder")} />
          </FormField>
        </div>
      </AccordionItem>
    );
  }

  if (title === "Bank") {
    return (
      <AccordionItem key={title} title={title}>
        <SmartFilterFields form={form} prefix="bank" includeDocs={false} />
      </AccordionItem>
    );
  }

  if (title === "Fixed Assets") {
    return (
      <AccordionItem key={title} title={title}>
        <SmartFilterFields form={form} prefix="fixedAssets" />
      </AccordionItem>
    );
  }

  if (title === "E-Signatures") {
    return <ESignaturesSection key={title} title={title} form={form} />;
  }

  if (title === "Product Description") {
    return <ProductDescriptionSection key={title} title={title} form={form} />;
  }

  if (title === "Template / Draft") {
    return (
      <AccordionItem key={title} title={title}>
        <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
          {TEMPLATE_DRAFT_MODULES.map(([key, label]) => (
            <label key={key} className="flex items-center gap-2 text-sm text-fg">
              <Checkbox {...form.register(`templateDraft.${key}` as const)} />
              {label} — template
            </label>
          ))}
        </div>
      </AccordionItem>
    );
  }

  if (title === "Last Rate") {
    return (
      <AccordionItem key={title} title={title}>
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-fg-muted">
                <th className="py-2 pr-4">Document type</th>
                <th className="py-2 pr-4">Add/Edit</th>
                <th className="py-2">View</th>
              </tr>
            </thead>
            <tbody>
              {LAST_RATE_TYPES.map((docType) => (
                <tr key={docType} className="border-b border-border/60">
                  <td className="py-2 pr-4 font-medium">{docType}</td>
                  <td className="py-2 pr-4">
                    <Checkbox {...form.register(`lastRate.${docType}.addEdit` as const)} />
                  </td>
                  <td className="py-2">
                    <Checkbox {...form.register(`lastRate.${docType}.view` as const)} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </AccordionItem>
    );
  }

  if (
    AUTO_CODE_ENTITIES.some(([, label]) => label === title)
  ) {
    const entityKey = AUTO_CODE_ENTITIES.find(([, label]) => label === title)?.[0];
    if (entityKey) {
      return <AutoCodeBlock key={title} form={form} entityKey={entityKey} title={title} />;
    }
  }

  return null;
}

function ESignaturesSection({
  title,
  form,
}: {
  title: string;
  form: UseFormReturn<SmartSettingsPayload>;
}) {
  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "eSignatures",
  });

  return (
    <AccordionItem title={title}>
      <div className="space-y-3">
        {fields.map((field, index) => (
          <div
            key={field.id}
            className="grid grid-cols-1 gap-3 rounded border border-border p-3 md:grid-cols-3"
          >
            <FormField label="Name">
              <Input {...form.register(`eSignatures.${index}.name` as const)} />
            </FormField>
            <FormField label="Signature URL">
              <Input {...form.register(`eSignatures.${index}.signatureUrl` as const)} />
            </FormField>
            <div className="flex items-end">
              <Button type="button" variant="outline" size="sm" onClick={() => remove(index)}>
                Remove
              </Button>
            </div>
          </div>
        ))}
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => append({ name: "", signatureUrl: "" })}
        >
          + Add more
        </Button>
      </div>
    </AccordionItem>
  );
}

function ProductDescriptionSection({
  title,
  form,
}: {
  title: string;
  form: UseFormReturn<SmartSettingsPayload>;
}) {
  const { fields, append, remove } = useFieldArray({
    control: form.control,
    name: "productDescription",
  });

  return (
    <AccordionItem title={title}>
      <div className="space-y-3">
        {fields.length === 0 ? (
          <p className="text-sm text-fg-muted">
            No description columns configured. Add rows to map display labels to document types.
          </p>
        ) : null}
        {fields.map((field, index) => (
          <div
            key={field.id}
            className="grid grid-cols-1 gap-3 rounded border border-border p-3 md:grid-cols-4"
          >
            <FormField label="Display name">
              <Input {...form.register(`productDescription.${index}.displayName` as const)} />
            </FormField>
            <FormField label="Label">
              <Input {...form.register(`productDescription.${index}.label` as const)} />
            </FormField>
            <FormField label="Width">
              <Input {...form.register(`productDescription.${index}.width` as const)} />
            </FormField>
            <FormField label="Transaction types (comma-separated)">
              <Input
                placeholder="SI, SC, VI, PO"
                {...form.register(`productDescription.${index}.transactionTypes` as const)}
              />
            </FormField>
            <div className="md:col-span-4">
              <Button type="button" variant="outline" size="sm" onClick={() => remove(index)}>
                Remove row
              </Button>
            </div>
          </div>
        ))}
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() =>
            append({
              displayName: "",
              label: "",
              width: "",
              transactionTypes: "",
            })
          }
        >
          + Add more
        </Button>
      </div>
    </AccordionItem>
  );
}
