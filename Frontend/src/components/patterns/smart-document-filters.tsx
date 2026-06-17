"use client";

import type { UseFormRegister, FieldValues, Path } from "react-hook-form";

import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { useSmartFilterLabels, type SmartModule } from "@/lib/hooks/use-smart-filter-labels";

interface SmartDocumentFiltersProps<T extends FieldValues> {
  module: SmartModule;
  register: UseFormRegister<T>;
  namePrefix?: string;
  includeDocs?: boolean;
}

export function SmartDocumentFilters<T extends FieldValues>({
  module,
  register,
  namePrefix = "smartFilters",
  includeDocs = true,
}: SmartDocumentFiltersProps<T>) {
  const { labels } = useSmartFilterLabels(module);

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      {(["filter1", "filter2", "filter3", "filter4"] as const).map((key) => (
        <FormField key={key} label={labels[key]}>
          <Input {...register(`${namePrefix}.${key}` as Path<T>)} />
        </FormField>
      ))}
      {includeDocs
        ? (["doc1", "doc2", "doc3", "doc4"] as const).map((key) => (
            <FormField key={key} label={labels[key]}>
              <Input {...register(`${namePrefix}.${key}` as Path<T>)} />
            </FormField>
          ))
        : null}
    </div>
  );
}
