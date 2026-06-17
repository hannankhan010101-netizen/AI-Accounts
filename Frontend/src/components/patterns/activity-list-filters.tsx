"use client";

import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import type { ActivityListParams } from "@/lib/api/tenant";

const SALES_DOC_TYPES = [
  "Sale Invoice",
  "Sale Receipt",
  "Sale Credit",
  "Quotation",
  "Sales Order",
  "PDC Received",
  "Delivery Note",
] as const;

const PURCHASES_DOC_TYPES = [
  "Purchase Invoice",
  "Supplier Payment",
  "Supplier Credit",
  "Purchase Order",
  "PDC Issued",
  "GRN",
] as const;

export interface ActivityFilterState extends ActivityListParams {
  includePlanning?: boolean;
}

interface ActivityListFiltersProps {
  kind: "sales" | "purchases";
  value: ActivityFilterState;
  onChange: (next: ActivityFilterState) => void;
  partyOptions: { id: string; label: string }[];
  statusOptions: string[];
}

export function ActivityListFilters({
  kind,
  value,
  onChange,
  partyOptions,
  statusOptions,
}: ActivityListFiltersProps) {
  const docTypes = kind === "sales" ? SALES_DOC_TYPES : PURCHASES_DOC_TYPES;
  const partyLabel = kind === "sales" ? "Customer" : "Supplier";

  return (
    <div className="mb-3 grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-5">
      <FormField label="Date from">
        <Input
          type="date"
          value={value.dateFrom ?? ""}
          onChange={(e) => onChange({ ...value, dateFrom: e.target.value || undefined })}
        />
      </FormField>
      <FormField label="Date to">
        <Input
          type="date"
          value={value.dateTo ?? ""}
          onChange={(e) => onChange({ ...value, dateTo: e.target.value || undefined })}
        />
      </FormField>
      <FormField label={partyLabel}>
        <Select
          value={value.partyId ?? ""}
          onChange={(e) => onChange({ ...value, partyId: e.target.value || undefined })}
        >
          <option value="">All</option>
          {partyOptions.map((p) => (
            <option key={p.id} value={p.id}>
              {p.label}
            </option>
          ))}
        </Select>
      </FormField>
      <FormField label="Type">
        <Select
          value={value.docType ?? ""}
          onChange={(e) => onChange({ ...value, docType: e.target.value || undefined })}
        >
          <option value="">All types</option>
          {docTypes.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </Select>
      </FormField>
      <FormField label="Status">
        <Select
          value={value.status ?? ""}
          onChange={(e) => onChange({ ...value, status: e.target.value || undefined })}
        >
          <option value="">All statuses</option>
          {statusOptions.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </Select>
      </FormField>
    </div>
  );
}
