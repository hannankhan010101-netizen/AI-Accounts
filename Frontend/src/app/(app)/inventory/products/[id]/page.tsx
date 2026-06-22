/** Product detail — overview, units, attachments */
"use client";

import Image from "next/image";
import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useMutation } from "@tanstack/react-query";

import { AttachmentPanel } from "@/components/patterns/attachment-panel";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { PageHeader } from "@/components/ui/page-header";
import { WorkspaceLoading } from "@/components/ui/workspace-loading";
import { useTenantListQuery, invalidateTenantQueries } from "@/lib/api/tenant-query";
import { attachmentsApi, inventoryApi, type ProductUomRow } from "@/lib/api/tenant";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { useQueryClient } from "@tanstack/react-query";

const TABS = [
  { id: "overview", label: "Overview" },
  { id: "units", label: "Units" },
  { id: "attachments", label: "Attachments" },
] as const;

export default function ProductDetailPage() {
  const params = useParams<{ id: string }>();
  const productId = params.id;
  const router = useRouter();
  const searchParams = useSearchParams();
  const tab = (searchParams.get("tab") as (typeof TABS)[number]["id"]) || "overview";
  const qc = useQueryClient();

  const { data, isLoading, error } = useTenantListQuery(
    ["product", productId],
    () => inventoryApi.getProduct(productId),
    { enabled: Boolean(productId) },
  );
  const product = data?.result;

  const archiveMutation = useMutation({
    mutationFn: () =>
      product?.isArchived
        ? inventoryApi.restoreProduct(productId)
        : inventoryApi.archiveProduct(productId),
    onSuccess: () => {
      invalidateTenantQueries(qc, "product", productId);
      invalidateTenantQueries(qc, "products");
    },
  });

  if (isLoading) return <WorkspaceLoading />;
  if (error || !product) {
    return <p className="text-sm text-status-danger">Could not load product.</p>;
  }

  const imageUrl = product.primaryImageAttachmentId
    ? attachmentsApi.productImageUrl(product.primaryImageAttachmentId)
    : null;

  const uomColumns = responsiveListColumns<ProductUomRow>([
    { key: "unitCode", header: "Unit" },
    { key: "conversionFactor", header: "Conversion", align: "right" },
    { key: "salePrice", header: "Sale price", align: "right" },
    {
      key: "isDefault",
      header: "Default",
      render: (r) => (r.isDefault ? "Yes" : "—"),
    },
  ]);

  return (
    <div className="space-y-6">
      <PageHeader
        title={`${product.code ?? ""} — ${product.name}`}
        breadcrumb="Stock / Products / Detail"
        actions={
          <div className="flex flex-wrap gap-2">
            <Button variant="outline" asChild>
              <Link href="/inventory/products">← Products</Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href={`/inventory/products/${productId}/edit`}>Edit</Link>
            </Button>
            <Button
              variant="outline"
              disabled={archiveMutation.isPending}
              onClick={() => archiveMutation.mutate()}
            >
              {product.isArchived ? "Restore" : "Archive"}
            </Button>
          </div>
        }
      />

      <nav className="flex flex-wrap gap-2 border-b border-border pb-2">
        {TABS.map((t) => (
          <Button
            key={t.id}
            size="sm"
            variant={tab === t.id ? "default" : "ghost"}
            onClick={() => router.push(`/inventory/products/${productId}?tab=${t.id}`)}
          >
            {t.label}
          </Button>
        ))}
      </nav>

      {tab === "overview" ? (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-[12rem_1fr]">
          {imageUrl ? (
            <div className="relative h-48 w-48 overflow-hidden rounded-lg border border-border">
              <Image src={imageUrl} alt={product.name} fill className="object-cover" unoptimized />
            </div>
          ) : null}
          <dl className="grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-fg-muted">Status</dt>
              <dd>
                <Badge variant={product.isArchived ? "default" : "success"}>
                  {product.isArchived ? "Archived" : "Active"}
                </Badge>
              </dd>
            </div>
            <div>
              <dt className="text-fg-muted">Type</dt>
              <dd>{product.isStock === false ? "Service / non-stock" : "Stock product"}</dd>
            </div>
            <div>
              <dt className="text-fg-muted">Category</dt>
              <dd>{product.category || "—"}</dd>
            </div>
            <div>
              <dt className="text-fg-muted">Unit</dt>
              <dd>{product.unit || "EA"}</dd>
            </div>
            <div>
              <dt className="text-fg-muted">Sale price</dt>
              <dd className="tabular-nums">{product.salePrice ?? "0"}</dd>
            </div>
            <div>
              <dt className="text-fg-muted">Cost</dt>
              <dd className="tabular-nums">{product.cost ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-fg-muted">Low stock level</dt>
              <dd className="tabular-nums">{product.lowStockLevel ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-fg-muted">Bin location</dt>
              <dd>{product.binLocation || "—"}</dd>
            </div>
          </dl>
        </div>
      ) : null}

      {tab === "units" ? (
        <EnterpriseGrid<ProductUomRow>
          columns={uomColumns as GridColumn<ProductUomRow>[]}
          rows={product.uoms ?? []}
          emptyMessage="No alternate units — base unit only."
          getRowId={(r) => r.id ?? r.unitCode}
        />
      ) : null}

      {tab === "attachments" ? (
        <AttachmentPanel entityType="product" entityId={productId} title="Files & images" />
      ) : null}
    </div>
  );
}
