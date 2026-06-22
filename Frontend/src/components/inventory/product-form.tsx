"use client";

import { useEffect } from "react";
import { useForm, type UseFormReturn } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { Checkbox } from "@/components/ui/checkbox";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { useAutoCodePreview } from "@/lib/hooks/use-auto-code-preview";
import {
  productFormDefaults,
  productFormSchema,
  type ProductFormValues,
} from "@/lib/inventory/product-schema";
import type { Product } from "@/lib/api/tenant";

type ProductFormProps = {
  formId: string;
  mode: "create" | "edit";
  initialProduct?: Product | null;
  showOpeningStock?: boolean;
  canViewCost?: boolean;
  onSubmit: (values: ProductFormValues) => void;
  children?: React.ReactNode;
  form?: UseFormReturn<ProductFormValues>;
};

export function ProductForm({
  formId,
  mode,
  initialProduct,
  showOpeningStock = mode === "create",
  canViewCost = true,
  onSubmit,
  children,
  form: externalForm,
}: ProductFormProps) {
  const internalForm = useForm<ProductFormValues>({
    resolver: zodResolver(productFormSchema),
    defaultValues: productFormDefaults,
  });
  const form = externalForm ?? internalForm;

  const { enabled: autoCode, nextCode } = useAutoCodePreview("product", {
    onPreview: (code) => {
      if (mode === "create" && code && !form.getValues("code")) {
        form.setValue("code", code);
      }
    },
  });

  useEffect(() => {
    if (!initialProduct) return;
    form.reset({
      code: initialProduct.code ?? "",
      name: initialProduct.name ?? "",
      isStock: initialProduct.isStock !== false,
      unit: initialProduct.unit ?? "EA",
      category: (initialProduct.category as string) ?? "",
      salePrice: String(initialProduct.salePrice ?? ""),
      cost: String(initialProduct.cost ?? ""),
      lowStockLevel: String(initialProduct.lowStockLevel ?? ""),
      binLocation: (initialProduct.binLocation as string) ?? "",
      openingQty: "",
      openingRate: "",
    });
  }, [initialProduct, form]);

  const isStock = form.watch("isStock");

  return (
    <form
      id={formId}
      onSubmit={form.handleSubmit(onSubmit)}
      className="space-y-6"
    >
      <section className="space-y-4 rounded-lg border border-border bg-surface p-4">
        <h2 className="text-sm font-semibold text-fg">Identity</h2>
        {mode === "create" ? (
          <FormField
            label={autoCode ? "Code (auto)" : "Code"}
            required={!autoCode}
            error={form.formState.errors.code?.message}
          >
            <Input placeholder={nextCode ?? undefined} {...form.register("code")} />
          </FormField>
        ) : (
          <FormField label="Code">
            <Input value={initialProduct?.code ?? ""} readOnly disabled />
          </FormField>
        )}
        <FormField label="Name" required error={form.formState.errors.name?.message}>
          <Input {...form.register("name")} />
        </FormField>
        <FormField label="Category" error={form.formState.errors.category?.message}>
          <Input placeholder="e.g. Pharma" {...form.register("category")} />
        </FormField>
        <label className="flex items-center gap-2 text-sm text-fg">
          <Checkbox {...form.register("isStock")} />
          Stock product (counts in inventory; unchecked = service / non-stock)
        </label>
      </section>

      <section className="space-y-4 rounded-lg border border-border bg-surface p-4">
        <h2 className="text-sm font-semibold text-fg">Pricing & unit</h2>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <FormField label="Unit" required error={form.formState.errors.unit?.message}>
            <Input placeholder="EA" {...form.register("unit")} />
          </FormField>
          <FormField
            label="Sale price"
            required={isStock}
            error={form.formState.errors.salePrice?.message}
          >
            <Input inputMode="decimal" {...form.register("salePrice")} />
          </FormField>
          {canViewCost ? (
            <FormField label="Cost" error={form.formState.errors.cost?.message}>
              <Input inputMode="decimal" {...form.register("cost")} />
            </FormField>
          ) : null}
          <FormField label="Low stock level" error={form.formState.errors.lowStockLevel?.message}>
            <Input inputMode="decimal" {...form.register("lowStockLevel")} />
          </FormField>
          <FormField label="Bin location" error={form.formState.errors.binLocation?.message}>
            <Input {...form.register("binLocation")} />
          </FormField>
        </div>
      </section>

      {showOpeningStock && isStock ? (
        <section className="space-y-4 rounded-lg border border-border bg-surface p-4">
          <h2 className="text-sm font-semibold text-fg">Opening stock (optional)</h2>
          <p className="text-xs text-fg-muted">
            Set initial on-hand quantity when creating a new stock product.
          </p>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            <FormField label="Quantity" error={form.formState.errors.openingQty?.message}>
              <Input inputMode="decimal" {...form.register("openingQty")} />
            </FormField>
            <FormField label="Rate (defaults to cost)" error={form.formState.errors.openingRate?.message}>
              <Input inputMode="decimal" {...form.register("openingRate")} />
            </FormField>
          </div>
        </section>
      ) : null}

      {children}
    </form>
  );
}

export function productFormToCreateInput(values: ProductFormValues) {
  const openingQty = values.openingQty?.trim();
  return {
    code: values.code?.trim() || null,
    name: values.name.trim(),
    isStock: values.isStock,
    unit: values.unit.trim() || "EA",
    category: values.category?.trim() || null,
    salePrice: values.salePrice ? Number(values.salePrice) : 0,
    cost: values.cost ? Number(values.cost) : 0,
    lowStockLevel: values.lowStockLevel ? Number(values.lowStockLevel) : null,
    binLocation: values.binLocation?.trim() || null,
    openingStock:
      openingQty && Number(openingQty) > 0
        ? {
            quantity: Number(openingQty),
            rate: values.openingRate ? Number(values.openingRate) : undefined,
          }
        : undefined,
  };
}

export function productFormToUpdateInput(values: ProductFormValues) {
  return {
    name: values.name.trim(),
    isStock: values.isStock,
    unit: values.unit.trim() || "EA",
    category: values.category?.trim() || null,
    salePrice: values.salePrice ? Number(values.salePrice) : 0,
    cost: values.cost ? Number(values.cost) : 0,
    lowStockLevel: values.lowStockLevel ? Number(values.lowStockLevel) : null,
    binLocation: values.binLocation?.trim() || null,
  };
}
