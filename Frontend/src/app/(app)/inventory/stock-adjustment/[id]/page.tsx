"use client";
import { useTenantDetailQuery } from "@/lib/api/tenant-query";

import { useParams } from "next/navigation";


import {
  InventoryVoucherDetail,
  fmtQty,
  type InventoryLine,
} from "@/components/patterns/inventory-voucher-detail";
import { type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { inventoryWritesApi } from "@/lib/api/tenant";

import { DetailPageLoading } from "@/components/ui/detail-page-loading";

export default function StockAdjustmentDetailPage() {
  const params = useParams<{ id: string }>();
  const { data, isLoading, error } = useTenantDetailQuery(["stock-adjustment", params.id], () => inventoryWritesApi.getStockAdjustment(params.id), { enabled: Boolean(params.id) });

  if (isLoading) return <DetailPageLoading />;
  if (error instanceof Error)
    return (
      <div className="rounded-md border border-status-danger/30 bg-status-danger/10 p-3 text-sm text-status-danger">
        {error.message}
      </div>
    );

  const doc = data?.result;
  if (!doc) return null;

  const lines = (doc.lines ?? []) as InventoryLine[];

  const columns = responsiveListColumns<InventoryLine>([
    { key: "productCode", header: "Product" },
    { key: "locationCode", header: "Location", render: (r) => r.locationCode ?? "—" },
    {
      key: "quantityDelta",
      header: "Qty Δ",
      align: "right",
      render: (r) => fmtQty(r.quantityDelta),
    },
    { key: "unitCost", header: "Unit cost", align: "right" },
  ]);

  return (
    <InventoryVoucherDetail
      docLabel="Stock adjustment"
      breadcrumb="Stock / Adjustments / Detail"
      listHref="/inventory/stock-adjustment"
      voucherNumber={doc.voucherNumber}
      documentDate={doc.adjustmentDate}
      status={doc.status}
      fields={[{ label: "Reason", value: doc.reason }]}
      lines={lines}
      lineColumns={columns}
      notes={doc.notes}
      printHref={`/print/stock-adjustment/${params.id}`}
    />
  );
}
