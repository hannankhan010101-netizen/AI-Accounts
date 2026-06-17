"use client";

import { FormField } from "@/components/ui/form-field";
import { Select } from "@/components/ui/select";
import { useOpMethods } from "@/lib/hooks/use-op-methods";

type PaymentMethodFieldProps = {
  value: string;
  onChange: (value: string) => void;
  error?: string;
};

export function PaymentMethodField({ value, onChange, error }: PaymentMethodFieldProps) {
  const { methods, defaultMethod, isLoading } = useOpMethods();
  const effective = value || defaultMethod;

  return (
    <FormField label="Payment method (OP)" error={error}>
      <Select
        value={effective}
        disabled={isLoading || methods.length === 0}
        onChange={(e) => onChange(e.target.value)}
      >
        {methods.map((m) => (
          <option key={m.id} value={m.id}>
            {m.label}
          </option>
        ))}
      </Select>
    </FormField>
  );
}

export function readPaymentMethod(customFields: unknown): string | null {
  if (!customFields || typeof customFields !== "object") return null;
  const raw = (customFields as Record<string, unknown>).paymentMethod;
  return raw != null && String(raw).trim() ? String(raw) : null;
}
