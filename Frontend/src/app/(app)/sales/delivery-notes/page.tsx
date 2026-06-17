/** Delivery notes list — catalog §5 */
"use client";
import { useTenantListQuery } from "@/lib/api/tenant-query";


import { useMemo } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { EnterpriseGrid } from "@/components/ui/enterprise-grid";
import { responsiveListColumns } from "@/lib/grid/responsive-columns";
import { useConfiguredListColumns } from "@/lib/hooks/use-configured-list-columns";
import { buildGridExport } from "@/lib/export/grid-export";
import { ListToolbar } from "@/components/ui/list-toolbar";
import { PageHeader } from "@/components/ui/page-header";
import { useClientList } from "@/lib/hooks/use-client-list";
import { useCustomerNameMap } from "@/lib/hooks/use-party-name-map";
import { matchText } from "@/lib/list/document-list-filters";
import { deliveryApi, type DeliveryNote } from "@/lib/api/tenant";

export default function DeliveryNotesPage() {
  const router = useRouter();
  const customerNames = useCustomerNameMap();
  const { data, isLoading, error } = useTenantListQuery(["delivery-notes"], () => deliveryApi.listDeliveryNotes());

  const { search, setSearch, pageRows, pagination, filtered } = useClientList({
    rows: data?.result,
    syncUrl: true,
    filterFn: (r, q) => matchText([r.voucherNumber, customerNames.get(r.customerId), r.status], q),
  });

  const baseColumns = useMemo(
    () =>
      responsiveListColumns<DeliveryNote>([
        {
          key: "voucherNumber",
          header: "Voucher",
          sortable: true,
          sortAccessor: (r) => r.voucherNumber,
        },
        {
          key: "deliveryDate",
          header: "Date",
          sortable: true,
          sortAccessor: (r) => r.deliveryDate,
          render: (r) => new Date(r.deliveryDate).toLocaleDateString(),
        },
        {
          key: "customerId",
          header: "Customer",
          render: (r) => customerNames.get(r.customerId) ?? r.customerId,
        },
        { key: "status", header: "Status" },
      ]),
    [customerNames],
  );
  const columns = useConfiguredListColumns("delivery-note", baseColumns);

  return (
    <div>
      <PageHeader
        title="Delivery notes"
        breadcrumb="Sell / Delivery notes"
        actions={
          <Button asChild>
            <Link href="/sales/delivery-notes/new">New delivery note</Link>
          </Button>
        }
      />
      <ListToolbar search={search} onSearchChange={setSearch} />
      <EnterpriseGrid<DeliveryNote>
        columns={columns}
        rows={pageRows}
        loading={isLoading}
        error={error}
        listEntity="sales-delivery-note"
        isSearching={Boolean(search)}
        onRowClick={(r) => r.id && router.push(`/sales/delivery-notes/${r.id}`)}
        pagination={pagination}
        exportCsv={{ ...buildGridExport("delivery-notes", columns), rows: filtered }}
      />
    </div>
  );
}
