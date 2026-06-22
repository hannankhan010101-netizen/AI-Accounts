"use client";

import { useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import {
  ProductForm,
  productFormToCreateInput,
} from "@/components/inventory/product-form";
import { Button } from "@/components/ui/button";
import { PageHeader } from "@/components/ui/page-header";
import { attachmentsApi, inventoryApi } from "@/lib/api/tenant";
import { ApiError } from "@/lib/api/client";
import { useCompany } from "@/lib/auth/company-context";
import { hasMeaningfulMasterDraft } from "@/lib/hooks/document-draft-helpers";
import { useDocumentWorkspaceDraft } from "@/lib/hooks/use-document-workspace-draft";
import {
  productFormDefaults,
  productFormSchema,
  type ProductFormValues,
} from "@/lib/inventory/product-schema";

export default function InventoryAddPage() {
  const router = useRouter();
  const { companyId } = useCompany();
  const [submitError, setSubmitError] = useState<string | null>(null);
  const imageInputRef = useRef<HTMLInputElement>(null);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  const form = useForm<ProductFormValues>({
    resolver: zodResolver(productFormSchema),
    defaultValues: productFormDefaults,
  });
  const watched = form.watch();

  const { topBanner, clearDraftOnSuccess } = useDocumentWorkspaceDraft({
    scope: "inventory-add",
    companyId,
    form,
    values: watched,
    shouldPersist: (v) =>
      hasMeaningfulMasterDraft(v) ||
      Boolean(v.salePrice) ||
      Boolean(v.openingQty) ||
      v.isStock === false,
  });

  const mutation = useMutation({
    mutationFn: async (values: ProductFormValues) => {
      const created = await inventoryApi.createProduct(productFormToCreateInput(values));
      const id = created.result.id;
      if (imageFile) {
        const uploaded = await attachmentsApi.upload("product", id, imageFile);
        await inventoryApi.setPrimaryImage(id, uploaded.result.id as string);
      }
      return created.result;
    },
    onSuccess: (product) => {
      clearDraftOnSuccess();
      router.push(`/inventory/products/${product.id}`);
    },
    onError: (err) =>
      setSubmitError(err instanceof ApiError ? err.message : "Could not create product"),
  });

  return (
    <div className="space-y-4">
      {topBanner}
      <PageHeader
        title="Add product"
        breadcrumb="Home / Inventory / Add"
        description="Create a product with pricing, optional opening stock, and image."
        actions={
          <>
            <Button type="button" variant="outline" onClick={() => router.push("/inventory/products")}>
              Cancel
            </Button>
            <Button type="submit" form="inventory-add-form" disabled={mutation.isPending}>
              {mutation.isPending ? "Saving…" : "Save product"}
            </Button>
          </>
        }
      />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[minmax(0,1fr)_18rem]">
        <ProductForm
          formId="inventory-add-form"
          mode="create"
          showOpeningStock
          form={form}
          onSubmit={(values) => {
            setSubmitError(null);
            mutation.mutate(values);
          }}
        >
          {submitError ? (
            <div className="rounded-md border border-status-danger/30 bg-status-danger/10 px-3 py-2 text-sm text-status-danger">
              {submitError}
            </div>
          ) : null}
        </ProductForm>

        <aside className="space-y-4">
          <section className="rounded-lg border border-border bg-surface p-4">
            <h2 className="mb-3 text-sm font-semibold text-fg">Product image</h2>
            <input
              ref={imageInputRef}
              type="file"
              accept="image/jpeg,image/png,image/webp,image/gif"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (!file) return;
                setImageFile(file);
                setImagePreview(URL.createObjectURL(file));
              }}
            />
            {imagePreview ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={imagePreview}
                alt="Preview"
                className="mb-3 h-40 w-40 rounded-lg border border-border object-cover"
              />
            ) : (
              <div className="mb-3 flex h-40 w-40 items-center justify-center rounded-lg border border-dashed border-border text-xs text-fg-muted">
                No image selected
              </div>
            )}
            <Button
              type="button"
              size="sm"
              variant="outline"
              onClick={() => imageInputRef.current?.click()}
            >
              Choose image
            </Button>
            {imageFile ? (
              <Button
                type="button"
                size="sm"
                variant="ghost"
                className="ml-2"
                onClick={() => {
                  setImageFile(null);
                  setImagePreview(null);
                  if (imageInputRef.current) imageInputRef.current.value = "";
                }}
              >
                Clear
              </Button>
            ) : null}
            <p className="mt-2 text-xs text-fg-muted">JPEG, PNG, or WebP up to 5 MB. Uploaded on save.</p>
          </section>
        </aside>
      </div>
    </div>
  );
}
