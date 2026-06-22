"use client";

import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import {
  ProductForm,
  productFormToUpdateInput,
} from "@/components/inventory/product-form";
import {
  ProductCustomFields,
  customFieldValuesToPayload,
  type ProductCustomFieldDef,
} from "@/components/inventory/product-custom-fields";
import { ProductImageUpload } from "@/components/inventory/product-image-upload";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { WorkspaceLoading } from "@/components/ui/workspace-loading";
import { useTenantListQuery, useTenantReferenceQuery } from "@/lib/api/tenant-query";
import { customFieldsApi, inventoryApi } from "@/lib/api/tenant";
import { ApiError } from "@/lib/api/client";
import {
  productFormDefaults,
  productFormSchema,
  type ProductFormValues,
} from "@/lib/inventory/product-schema";

export default function EditProductPage() {
  const params = useParams<{ id: string }>();
  const productId = params.id;
  const router = useRouter();

  const { data, isLoading, error } = useTenantListQuery(
    ["product", productId],
    () => inventoryApi.getProduct(productId),
    { enabled: Boolean(productId) },
  );
  const product = data?.result;

  const { data: fieldDefsData } = useTenantReferenceQuery(
    ["custom-field-definitions", "product"],
    () => customFieldsApi.listDefinitions("product"),
  );
  const customFieldDefs = useMemo(
    () =>
      (fieldDefsData?.result ?? []).filter(
        (d) => d.entityType === "product",
      ) as ProductCustomFieldDef[],
    [fieldDefsData],
  );

  const [customFieldValues, setCustomFieldValues] = useState<Record<string, string>>({});

  const form = useForm<ProductFormValues>({
    resolver: zodResolver(productFormSchema),
    defaultValues: productFormDefaults,
  });

  useEffect(() => {
    if (!product?.customFields || typeof product.customFields !== "object") return;
    const initial: Record<string, string> = {};
    for (const [key, val] of Object.entries(product.customFields as Record<string, unknown>)) {
      if (val != null) initial[key] = String(val);
    }
    setCustomFieldValues(initial);
  }, [product]);

  const mutation = useMutation({
    mutationFn: (values: ProductFormValues) =>
      inventoryApi.updateProduct(productId, {
        ...productFormToUpdateInput(values),
        customFields: customFieldValuesToPayload(customFieldDefs, customFieldValues),
      }),
    onSuccess: () => router.push(`/inventory/products/${productId}`),
  });

  if (isLoading) return <WorkspaceLoading />;
  if (error || !product) {
    return <p className="text-sm text-status-danger">Could not load product.</p>;
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title={`Edit ${product.code ?? ""} — ${product.name}`}
        breadcrumb="Stock / Products / Edit"
        actions={
          <>
            <Button type="button" variant="outline" asChild>
              <Link href={`/inventory/products/${productId}`}>Cancel</Link>
            </Button>
            <Button type="submit" form="product-edit-form" disabled={mutation.isPending}>
              {mutation.isPending ? "Saving…" : "Save changes"}
            </Button>
          </>
        }
      />
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_18rem]">
        <div className="space-y-6">
          <ProductForm
            formId="product-edit-form"
            mode="edit"
            initialProduct={product}
            showOpeningStock={false}
            form={form}
            onSubmit={(values) => mutation.mutate(values)}
          >
            {mutation.isError ? (
              <p className="text-sm text-status-danger">
                {mutation.error instanceof ApiError
                  ? mutation.error.message
                  : "Could not save"}
              </p>
            ) : null}
          </ProductForm>
          <ProductCustomFields
            definitions={customFieldDefs}
            values={customFieldValues}
            onChange={(key, value) =>
              setCustomFieldValues((prev) => ({ ...prev, [key]: value }))
            }
          />
        </div>
        <aside className="rounded-lg border border-border bg-surface p-4">
          <h2 className="mb-3 text-sm font-semibold text-fg">Product image</h2>
          <ProductImageUpload
            productId={productId}
            attachmentId={product.primaryImageAttachmentId}
            onUploaded={(id) => void inventoryApi.setPrimaryImage(productId, id)}
            onRemoved={() => void inventoryApi.setPrimaryImage(productId, null)}
          />
        </aside>
      </div>
    </div>
  );
}
