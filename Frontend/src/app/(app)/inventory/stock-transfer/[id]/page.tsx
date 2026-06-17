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

export default function StockTransferDetailPage() {
  const params = useParams<{ id: string }>();
  const { data, isLoading, error } = useTenantDetailQuery(["stock-transfer", params.id], () => inventoryWritesApi.getStockTransfer(params.id), { enabled: Boolean(params.id) });

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
    {
      key: "quantity",
      header: "Quantity",
      align: "right",
      render: (r) => fmtQty(r.quantity),
    },
    { key: "unitCost", header: "Unit cost", align: "right" },
  ]);

  return (
    <InventoryVoucherDetail
      docLabel="Stock transfer"
      breadcrumb="Stock / Transfers / Detail"
      listHref="/inventory/stock-transfer"
      voucherNumber={doc.voucherNumber}
      documentDate={doc.transferDate}
      status={doc.status}
      fields={[
        { label: "From", value: doc.fromLocationCode },
        { label: "To", value: doc.toLocationCode },
      ]}
      lines={lines}
      lineColumns={columns}
      notes={doc.notes}
      printHref={`/print/stock-transfer/${params.id}`}
    />
  );
}
