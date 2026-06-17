"use client";

import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { useCustomerNameMap, useSupplierNameMap } from "@/lib/hooks/use-party-name-map";

export interface ReportCriteriaValue {
  dateFrom: string;
  dateTo: string;
  customerId?: string;
  supplierId?: string;
  productCode?: string;
  status?: string;
}

function schemaHasProperty(schema: Record<string, unknown> | undefined, key: string): boolean {
  const props = schema?.properties;
  if (!props || typeof props !== "object") return false;
  return key in (props as Record<string, unknown>);
}

export function ReportCriteriaFields({
  schema,
  value,
  onChange,
}: {
  schema?: Record<string, unknown>;
  value: ReportCriteriaValue;
  onChange: (next: ReportCriteriaValue) => void;
}) {
  const customerNames = useCustomerNameMap();
  const supplierNames = useSupplierNameMap();

  const showCustomer = schemaHasProperty(schema, "customerId");
  const showSupplier = schemaHasProperty(schema, "supplierId");
  const showProduct = schemaHasProperty(schema, "productCode");
  const showStatus = schemaHasProperty(schema, "status");

  if (!showCustomer && !showSupplier && !showProduct && !showStatus) {
    return null;
  }

  return (
    <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-4">
      {showCustomer ? (
        <FormField label="Customer">
          <Select
            value={value.customerId ?? ""}
            onChange={(e) => onChange({ ...value, customerId: e.target.value || undefined })}
          >
            <option value="">All customers</option>
            {[...customerNames.entries()].map(([id, name]) => (
              <option key={id} value={id}>
                {name}
              </option>
            ))}
          </Select>
        </FormField>
      ) : null}
      {showSupplier ? (
        <FormField label="Supplier">
          <Select
            value={value.supplierId ?? ""}
            onChange={(e) => onChange({ ...value, supplierId: e.target.value || undefined })}
          >
            <option value="">All suppliers</option>
            {[...supplierNames.entries()].map(([id, name]) => (
              <option key={id} value={id}>
                {name}
              </option>
            ))}
          </Select>
        </FormField>
      ) : null}
      {showProduct ? (
        <FormField label="Product code">
          <Input
            value={value.productCode ?? ""}
            placeholder="Optional"
            onChange={(e) => onChange({ ...value, productCode: e.target.value || undefined })}
          />
        </FormField>
      ) : null}
      {showStatus ? (
        <FormField label="Status">
          <Input
            value={value.status ?? ""}
            placeholder="e.g. posted"
            onChange={(e) => onChange({ ...value, status: e.target.value || undefined })}
          />
        </FormField>
      ) : null}
    </div>
  );
}
