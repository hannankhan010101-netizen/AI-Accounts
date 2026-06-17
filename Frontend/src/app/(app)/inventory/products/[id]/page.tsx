/** Product multi-UOM tiers — FA §7.1 */
"use client";
import { useTenantListQuery, invalidateTenantQueries } from "@/lib/api/tenant-query";


import { useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { FormField } from "@/components/ui/form-field";
import { Input } from "@/components/ui/input";
import { PageHeader } from "@/components/ui/page-header";
import { inventoryApi, type Product, type ProductUomRow } from "@/lib/api/tenant";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";

export default function ProductUomPage() {
  const params = useParams<{ id: string }>();
  const productId = params.id;
  const qc = useQueryClient();
  const [unitCode, setUnitCode] = useState("");
  const [conversionFactor, setConversionFactor] = useState("1");
  const [salePrice, setSalePrice] = useState("");
  const [isDefault, setIsDefault] = useState(false);

  const { data: products } = useTenantListQuery(["products"], () => inventoryApi.listProducts());
  const product = (products?.result ?? []).find((p) => p.id === productId) as Product | undefined;

  const { data, isLoading, error } = useTenantListQuery(["product-uoms", productId], () => inventoryApi.listProductUoms(productId),
    { enabled: Boolean(productId) });

  const save = useMutation({
    mutationFn: () =>
      inventoryApi.upsertProductUom(productId, {
        unitCode: unitCode.trim(),
        conversionFactor,
        salePrice: salePrice || String(product?.salePrice ?? "0"),
        isDefault,
      }),
    onSuccess: () => {
      setUnitCode("");
      setConversionFactor("1");
      setSalePrice("");
      setIsDefault(false);
      void invalidateTenantQueries(qc, "product-uoms", productId);
      void invalidateTenantQueries(qc, "products");
    },
  });

  const columns = responsiveListColumns<ProductUomRow>([
    { key: "unitCode", header: "Unit", sortable: true, sortAccessor: (r) => r.unitCode },
    { key: "conversionFactor", header: "Conversion", align: "right" },
    { key: "salePrice", header: "Sale price", align: "right" },
    {
      key: "isDefault",
      header: "Default",
      render: (r) => (r.isDefault ? "Yes" : "—"),
    },
  ] satisfies GridColumn<ProductUomRow>[]);

  const title = product ? `${product.code ?? ""} — ${product.name}` : "Product UOM";

  return (
    <div className="space-y-6">
      <PageHeader
        title={title}
        breadcrumb="Stock / Products / Units"
        description="Alternate units and conversion factors for this product."
        actions={
          <Link href="/inventory/products">
            <Button variant="outline">← Products</Button>
          </Link>
        }
      />

      <div className="max-w-md space-y-3 rounded-lg border border-border bg-surface p-4">
        <FormField label="Unit code">
          <Input value={unitCode} onChange={(e) => setUnitCode(e.target.value)} placeholder="BOX" />
        </FormField>
        <FormField label="Conversion factor (to base unit)">
          <Input
            value={conversionFactor}
            onChange={(e) => setConversionFactor(e.target.value)}
          />
        </FormField>
        <FormField label="Sale price">
          <Input
            value={salePrice}
            onChange={(e) => setSalePrice(e.target.value)}
            placeholder={String(product?.salePrice ?? "0")}
          />
        </FormField>
        <label className="flex items-center gap-2 text-sm">
          <Checkbox checked={isDefault} onChange={(e) => setIsDefault(e.target.checked)} />
          Default selling unit
        </label>
        <Button
          onClick={() => save.mutate()}
          disabled={save.isPending || !unitCode.trim()}
        >
          Save unit
        </Button>
        {save.isError ? (
          <p className="text-sm text-status-danger">
            {save.error instanceof Error ? save.error.message : "Save failed"}
          </p>
        ) : null}
      </div>

      <EnterpriseGrid<ProductUomRow>
        columns={columns}
        rows={data?.result ?? []}
        loading={isLoading}
        error={error}
        emptyMessage="No alternate units — base unit only."
        getRowId={(r) => r.id ?? r.unitCode}
      />
    </div>
  );
}
