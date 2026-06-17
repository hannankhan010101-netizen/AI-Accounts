/** Supplier payments list — catalog §6.4 */
"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useMemo } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { EnterpriseGrid, type GridColumn } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { useConfiguredListColumns } from "@/lib/hooks/use-configured-list-columns";
import { buildGridExport } from "@/lib/export/grid-export";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { PageHeader } from "@/components/ui/page-header";
import { useClientList } from "@/lib/hooks/use-client-list";
import { useSupplierNameMap } from "@/lib/hooks/use-party-name-map";
import { matchText } from "@/lib/list/document-list-filters";
import { purchasesApi, type SupplierPayment } from "@/lib/api/tenant";

export default function SupplierPaymentsPage() {
  const router = useRouter();
  const supplierNames = useSupplierNameMap();
  const { data, isLoading, error } = useTenantListQuery(["supplier-payments"], () => purchasesApi.listSupplierPayments());

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) => matchText([r.voucherNumber as string, supplierNames.get(r.supplierId)], q),
  });

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<SupplierPayment>([
        { key: "voucherNumber", header: "Voucher" },
        {
          key: "paymentDate",
          header: "Date",
          render: (r) => new Date(r.paymentDate).toLocaleDateString(),
        },
        {
          key: "supplierId",
          header: "Supplier",
          render: (r) => supplierNames.get(r.supplierId) ?? r.supplierId,
        },
        { key: "totalAmount", header: "Amount", align: "right" },
        {
          key: "unallocatedBalance",
          header: "Balance",
          align: "right",
          sortable: true,
          sortAccessor: (r) => Number(r.unallocatedBalance ?? 0),
          render: (r) => {
            const bal = r.unallocatedBalance;
            if (bal == null || bal === "") return "—";
            const n = Number(bal);
            return n > 0.009 ? n.toFixed(2) : "—";
          },
        },
        {
          key: "return",
          header: "",
          render: (r) => {
            const n = Number(r.unallocatedBalance ?? 0);
            if (n <= 0.009 || !r.id) return null;
            return (
              <Link
                href={`/purchases/payments/${r.id}/return-advance`}
                className="text-brand hover:underline"
                onClick={(e) => e.stopPropagation()}
              >
                Return
              </Link>
            );
          },
        },
        { key: "journalId", header: "Posted", render: (r) => (r.journalId ? "Yes" : "—") },
      ]),
    [supplierNames],
  );
  const columns = useConfiguredListColumns("supplier-payment", baseColumns);

  return (
    <div>
      <PageHeader
        title="Bill payments"
        breadcrumb="Buy / Payments"
        tourRoot="supplier-payments-header"
        tourActions="supplier-payments-new"
        actions={
          <Button asChild>
            <Link href="/purchases/payments/new">New payment</Link>
          </Button>
        }
      />
      <ListToolbar search={search} onSearchChange={setSearch} />
      <EnterpriseGrid<SupplierPayment>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        listEntity="purchase-payment"
        isSearching={Boolean(search)}
        onRowClick={(r) => r.id && router.push(`/purchases/payments/${r.id}`)}
        pagination={pagination}
        exportCsv={{ ...buildGridExport("supplier-payments", columns), rows: filtered }}
      />
    </div>
  );
}
